from __future__ import annotations

import logging
import os
import signal
import socket
from enum import Enum
from multiprocessing import Event
from queue import Empty, Queue
from threading import Thread
from time import sleep, time_ns
from typing import Any

import mltraq
from mltraq.experiment import ExperimentNotFoundException
from mltraq.opts import options
from mltraq.run import Run
from mltraq.session import Session
from mltraq.storage import serialization
from mltraq.storage.database import Database
from mltraq.utils.bunch import Bunch
from mltraq.utils.enums import enforce_enum
from mltraq.utils.exceptions import ExceptionWithMessage, FatalError, InvalidInput, ServiceExit, service_shutdown
from mltraq.utils.sequence import Sequence

log = logging.getLogger(__name__)

DataStreamKind = Enum("DataStreamKind", ["UNIX", "INET"])


class TooBigException(ExceptionWithMessage):
    """
    Handling of messages too big to be sent by the specified DataStreamKind.
    """

    pass


def resolve_inet_address(address: str) -> str:
    """
    Given an INET `address` eg "x.yz", resolve it to an IP address.
    """
    addrinfo = socket.getaddrinfo(address[0], address[1], proto=socket.IPPROTO_UDP)
    if len(addrinfo) < 1:
        raise InvalidInput(f"Address '{address}' cannot be resolved.")
    return addrinfo[0][4]


class DataStreamServer:
    """
    Server handling incoming messages, using two threads:

    - DataStreamServer: Handling of incoming messages, adding them to a queue of deserialized messages.
    - DatabaseWriter: Consuming batches of deserialized messages, adding them to the database.

    The two activities are decoupled s.t. inserts in the database do not impact the reception of new messages.
    """

    __slots__ = ("db", "stats", "ready", "kind", "bufsize", "address", "terminate", "received", "thread", "sock", "dbw")

    def __init__(self, db: Database | None = None):
        """
        Initialize a new server, linking it to the specified `db`. The `db` object is expected to not be actively
        used by other threads.
        """
        self.db = db if db else Database()
        self.thread = None

    def thread_main(self):
        """
        Handle the incoming messages. This is executed as the thread main function and it blocks.
        It starts the thread handled by `DatabaseWriter`.
        """

        # Initialize stats
        self.stats = Bunch()
        self.stats.time_begin = time_ns()
        self.stats.count_messages = 0

        # Start database writer thread
        self.dbw = DatabaseWriter(self.db)
        self.dbw.start()

        # Handle incoming messages (blocking)
        self.recv_handler(lambda obj: self.dbw.messages.put(obj))

        # Cleanup
        self.cleanup()

    def recv_handler(self, func: callable):
        """
        Handle incoming messages, reading them, deserializing them,
        and passing them to `func`.

        It sets the event `self.ready`, signaling that the thread is now
        ready to read new messages from the socket.

        The function can be interrupted by setting the event `self.terminate`.
        """

        log.debug(f"{self.__class__.__name__}: Waiting for messages")
        delay = options().get("datastream.srv_throttle_recv")
        self.ready.set()
        while not self.terminate.is_set():
            try:
                data, address = self.sock.recvfrom(self.bufsize)
                self.received.set()
            except BlockingIOError:
                # Nothing to read! loop, s.t. we can check the state
                # of `self.terminate``.
                sleep(delay)
                continue
            self.stats.count_messages += 1
            obj = serialization.deserialize(data)
            func(obj)
            sleep(delay)

    def update_stats(self):
        """
        Update stats.
        """
        self.stats.time_end = time_ns()
        self.stats.elapsed = self.stats.time_end - self.stats.time_begin
        self.stats.rate = self.stats.count_messages / (self.stats.elapsed / 10**9)

    def start(self, blocking=False) -> DataStreamServer:
        """
        Start the server, `blocking` if set to True.
        It starts the thread running `process_messages()`.
        """

        # Initialize listening socket
        self.kind = enforce_enum(options().get("datastream.kind"), DataStreamKind)
        if self.kind == DataStreamKind["UNIX"]:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.address = options().get("datastream.srv_address")
            self.bufsize = 4096
        elif self.kind == DataStreamKind["INET"]:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.address = resolve_inet_address(options().get("datastream.srv_address").split(":"))
            self.bufsize = 1500
        else:
            raise InvalidInput(f"Unknown datastream kind: {self.kind.name}")

        if self.kind == DataStreamKind["UNIX"]:
            try:
                os.unlink(self.address)
                log.warning(f"{self.__class__.__name__}: Relinked stale '{self.address}'")
            except OSError:
                pass

        try:
            self.sock.bind(self.address)
        except OSError as e:
            raise FatalError(f"Address '{self.address}' not available") from e

        log.debug(f"Listening on '{options().get('datastream.srv_address')}' ({self.kind.name})")

        # Set socket not blocking (we also need to check some events in the thread loop).
        self.sock.setblocking(0)

        # Start thread to process incoming messages
        self.terminate = Event()
        self.ready = Event()
        self.received = Event()
        self.thread = Thread(target=self.thread_main, name="DataStreamServer")
        self.thread.start()

        # Wait until ready to receive messages.
        self.ready.wait()

        # If blocking, do not return.
        if blocking:
            while True:
                sleep(0.1)

        return self

    def cleanup(self):
        """
        Executed by the thread to clean up its state before exiting.
        """

        log.debug(f"{self.__class__.__name__}: Cleanup ...")
        self.update_stats()
        log.debug(
            f"{self.__class__.__name__}: Stats: count_messages="
            f"{self.stats.count_messages} rate={self.stats.rate:.2f} messages/s"
        )
        self.sock.close()
        if self.kind == DataStreamKind["UNIX"]:
            os.unlink(self.address)
        self.dbw.stop()

    def stop(self):
        """
        Requests the termination of the thread. It blocks until the thread terminates.
        """
        log.debug(f"{self.__class__.__name__}: Requested termination ...")

        if self.thread and self.thread.is_alive():
            self.terminate.set()
            self.thread.join()
        log.debug(f"{self.__class__.__name__}: Terminated")


class DataStreamClient:
    """
    Sends messages to the server. No threads. It uses UNIX/INET datagrams, relying
    on the system buffer. If messages are sent too frequently, some of them will be lost.
    """

    __slots__ = ("kind", "run", "send_delay", "sock", "bufsize", "address", "stats")

    def __init__(
        self,
        run: Run | None = None,
    ):
        """
        Link the client to a `run`.
        """

        self.run = run
        self.kind = enforce_enum(options().get("datastream.kind"), DataStreamKind)
        self.send_delay = options().get("datastream.cli_throttle_send")

        if self.kind == DataStreamKind["UNIX"]:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.address = options().get("datastream.cli_address")
            self.bufsize = 4096
        elif self.kind == DataStreamKind["INET"]:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Resolve the address once, s.t. it doesn't need to be resolved at every send.
            self.address = resolve_inet_address(options().get("datastream.cli_address").split(":"))
            self.bufsize = 1500
        else:
            raise InvalidInput(f"Unknown datastream kind: {self.kind}")

        log.debug(f"Streaming to '{options().get('datastream.cli_address')}' ({self.kind.name})")

        self.stats = Bunch()
        self.stats.time_begin = time_ns()
        self.stats.count_errors = 0
        self.stats.count_messages = 0

    def send(self, obj: Any):
        """
        Serialize `obj` and send it.
        """
        data = serialization.serialize(obj)
        if len(data) > self.bufsize:
            raise TooBigException(
                f"Too much data to send: {len(data)} > {self.bufsize} (solution: reduce the contents of the sequence)"
            )
        try:
            self.stats.count_messages += 1
            self.sock.sendto(data, self.address)
        except OSError:
            # Likely "[Errno 55] No buffer space available"
            self.stats.count_errors += 1
            pass
        sleep(self.send_delay)

    def send_sequence(self, record: dict):
        """
        Send `record` of Sequence, s.t. the state of the remote object can be updated.
        `record` contains two keys, `field_name` and `record`.

        The inner `record` contains at least keys `idx` and `timestamp`.
        `idx` can be used to identify lost messages.
        """

        field_name = record["field_name"]
        record = record["record"]

        self.send(
            {
                "id_experiment": self.run.id_experiment,
                "id_run": self.run.id_run,
                "field_name": field_name,
                "record": record,
            }
        )

    def cleanup(self):
        """
        Cleaning up of the client, closing the socket and updating the stats.
        """
        self.sock.close()
        self.update_stats()
        log.debug(f"{self.__class__.__name__}: Closing")
        log.debug(
            f"{self.__class__.__name__}: Stats: "
            f"count_messages={self.stats.count_messages} "
            f"rate={self.stats.rate:.2f} messages/s "
            f"count_errors={self.stats.count_errors}"
        )

    def update_stats(self):
        """
        Update the stats.
        """
        self.stats.time_end = time_ns()
        self.stats.elapsed = self.stats.time_end - self.stats.time_begin
        self.stats.rate = self.stats.count_messages / (self.stats.elapsed / 10**9)


class DatabaseWriter:
    """
    Handling of database writes. Whenever a new experiment is seen in the messages, it tries to load
    its state from the database, and it adds new records to the specified run/sequence.
    Regularly, it persists the updated experiment.
    """

    __slots__ = ("batch", "session", "messages", "experiments", "terminate", "received", "thread")

    def __init__(self, db: Database):
        """
        Create a new instance linked to `db`, which is then binded to a session to load/persist experiments.
        """
        self.batch = []
        self.session = Session(db=db)
        self.experiments = {}
        self.thread = None

    def thread_main(self):
        """
        Check for new messages, and if any, process them.
        """

        delay = options().get("datastream.srv_throttle_persist")

        # Introduce an initial delay to let the initial
        # burst of messages to flow in, useful for demos/tests.
        sleep(delay)

        while not self.terminate.is_set():
            try:
                if not self.messages.empty():
                    n_messages = self.messages.qsize()
                    # Process `n_messages`` messages, that are guaranteed to exist without blocking.
                    for _ in range(n_messages):
                        self.batch.append(self.messages.get())
                    self.process_batch()
                    # Wait at least `delay` seconds. `process_batch` persists the experiments to database,
                    # we don't want to do it too often.
                    sleep(delay)
            except Empty:
                pass
        self.cleanup()

    def process_batch(self):
        """
        Process all messages, persisting the updated experiments.
        """

        if len(self.batch) == 0:
            log.debug(f"{self.__class__.__name__}: No new messages to process")
            return

        id_experiments = set()
        for message in self.batch:
            try:
                # The experiment and run must already exist in the db.
                if message["id_experiment"] not in self.experiments:
                    self.experiments[message["id_experiment"]] = self.session.load(
                        id_experiment=message["id_experiment"]
                    )
                run = self.experiments[message["id_experiment"]].runs[message["id_run"]]

                # If the sequence with field_name doesn't exist, add it.
                if message["field_name"] not in run.fields:
                    run.fields[message["field_name"]] = Sequence()
                sequence: Sequence = run.fields[message["field_name"]]

            except (ExperimentNotFoundException, AttributeError, KeyError):
                # We received a message that cannot be matched to an existing experiment/run/field, ignore it.
                log.error(
                    f"Invalid message: id_experiment='{message['id_experiment']}' "
                    f"id_run='{message['id_run']}' field_name='{message['field_name']}'"
                )
                continue

            # Add the record to the sequence
            sequence.stream_recv(message["record"])

            # Keep track of seen experiment IDs
            id_experiments.add(message["id_experiment"])

        # Persist only experiments that received new records.
        for id_experiment in id_experiments:
            self.experiments[id_experiment].persist(if_exists="replace")

        log.debug(
            f"{self.__class__.__name__}: Processed {len(self.batch)} new messages for {len(id_experiments)} experiments"
        )
        self.batch.clear()
        self.received.set()

    def start(self) -> DatabaseWriter:
        """
        Start a new DatabaseWriter thread.
        """
        self.messages = Queue()
        self.terminate = Event()
        self.received = Event()
        self.thread = Thread(target=self.thread_main, name="DatabaseWriter")
        self.thread.start()
        return self

    def stop(self):
        """
        Request the termination of the thread.
        """
        log.debug(f"{self.__class__.__name__}: Requested termination ...")

        if self.thread and self.thread.is_alive():
            self.terminate.set()
            self.thread.join()
        log.debug(f"{self.__class__.__name__}: Terminated")

    def cleanup(self):
        """
        Called by the thread to clean up its internal state before termination.
        """
        self.process_batch()


def datastream_server():
    """
    Starts a datastream server, called by the CLI tool.
    """

    log.info(f"Starting MLtraq DataStream server (PID: {os.getpid()})")

    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    try:
        session = mltraq.create_session()
        ds = DataStreamServer(session.db)
        ds.start(blocking=True)
    except ServiceExit:
        ds.stop()
