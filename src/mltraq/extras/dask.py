import time
from asyncio.exceptions import CancelledError
from datetime import datetime
from typing import Callable, Dict, Union

import dask
from dask.distributed import Client
from IPython.display import clear_output, display
from mltraq.options import options
from mltraq.run import Run
from mltraq.storage import serialization
from mltraq.utils.log import default_exception_handler, init_logging, logger


def log_event(msg: Union[Dict, str]):
    """Log structured event with Dask.

    Args:
        msg (Union[Dict, str]): Event to log.
    """
    dask.distributed.get_worker().log_event("MLTRAQ", msg)


def dask_logger(run: Run, insert_delay: float = 0) -> Run:
    """Dask logger function that can be appended on experiments,
    to log the attributes of executed runs with Dask, enabling
    real-time experiment tracking. Tracked properties:

    Args:
        run (Run): Run to track.
        insert_delay (float, optional): Introduce a delay (seconds),
            useful to demonstrate the tracking functionality. Defaults to 0.

    Returns:
        Run: unaltered run after tracking it.
    """
    if insert_delay > 0:
        time.sleep(insert_delay)

    # Dask doesn't know how to serialize the uuid.UUID type, Pandas data frames, etc.0
    log_event({"id_run": str(run.id_run), "fields": serialization.serialize(run.fields)})
    return run


@default_exception_handler
def monitor_latest_event(client_address: str = None):
    """Utility function to report the latest tracked Run event, useful to start
    debugging execution issues. The function returns after a keyboard interrupt
    or after the connection with the scheduler is lost, which can happen if:
    1. The connection delay is too low (see dask)
    2. The Dask scheduler terminated, either nicely or after a failure

    Args:
        client_address (str, optional): Dask scheduler address. Defaults to dask.scheduler_address.
    """

    if client_address is None:
        client_address = options.get("dask.scheduler_address")

    init_logging()

    def display_progress(events):
        clear_output(wait=True)
        print(f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} Count events: {len(events)}\n")  # noqa
        # Display fields of last received record
        last_run_fields = serialization.deserialize(events[-1][1]["fields"])
        display(last_run_fields)

    monitor_events(display_progress, client_address=client_address)


@default_exception_handler
def monitor_events(func: Callable, client_address: str = None):
    """Utility function to execute a callable, passing a Pandas dataframe as argument, representing
    all the tracked events. It can be used to implement custom tracking monitors.

    Args:
        func (Callable): Function that accepts as argument a Pandas dataframe, representing the
        tracked events.
        client_address (str, optional): _description_. Defaults to dask.scheduler_address.
    """

    if client_address is None:
        client_address = options.get("dask.scheduler_address")

    try:
        with Client(address=client_address, timeout=options.get("dask.client_timeout")) as client:
            while True:
                events = client.get_events("MLTRAQ")
                func(events)
                time.sleep(1)
    except (CancelledError, OSError):
        logger.error("Connection failed or cluster terminated")
