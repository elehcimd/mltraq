import logging
from multiprocessing import Event
from os import sep
from threading import Thread

import psutil

from mltraq.opts import options
from mltraq.utils.sequence import Sequence

log = logging.getLogger(__name__)


class SystemMonitor:
    def __init__(self, sequence: Sequence):
        self.thread = None
        self.sequence = sequence
        pass

    def start(self):
        self.terminate = Event()
        self.produced = Event()
        self.thread = Thread(target=self.thread_main, name="SystemMonitor")
        self.thread.start()
        return self

    def thread_main(self):
        interval = options().get("sysmon.interval")
        percpu = options().get("sysmon.percpu")
        path = options().get("sysmon.path")

        while not self.terminate.is_set():
            self.sequence.append(**get_stats(path=path, interval=interval, percpu=percpu))
            self.produced.set()

    def stop(self):
        """
        Requests the termination of the thread. It blocks until the thread terminates.
        """
        log.debug(f"{self.__class__.__name__}: Requested termination ...")

        if self.thread and self.thread.is_alive():
            self.terminate.set()
            self.thread.join()
        log.debug(f"{self.__class__.__name__}: Terminated")

    def cleanup(self):
        pass


def get_stats(path: str = sep, interval: float = 1, percpu: bool = False):
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(path)
    net_begin = psutil.net_io_counters()

    # this blocks for `interval` seconds, capturing stats for CPU and (implicitly) network.
    cpu = psutil.cpu_percent(interval=interval, percpu=True)

    net_end = psutil.net_io_counters()
    stats_cpu = {"cpu_pct": int(sum(cpu) / len(cpu) * 10) / 10}
    if percpu:
        stats_cpu |= {f"cpu{idx}_pct": pct for idx, pct in enumerate(cpu)}
    stats_mem = {
        "mem_total_gb": round(mem.total / 1e9, 2),
        "mem_free_gb": round(mem.available / 1e9, 2),
        "mem_used_pct": mem.percent,
    }
    stats_disk = {
        "disk_total_gb": round(disk.total / 1e9, 2),
        "disk_free_gb": round(disk.free / 1e9, 2),
        "disk_used_pct": round((disk.total - disk.free) / disk.total * 1e2, 2),
    }
    stats_net = {
        "net_recv_kbs": round((net_end.bytes_recv - net_begin.bytes_recv) / interval / 1e3, 2),
        "net_sent_kbs": round((net_end.bytes_sent - net_begin.bytes_sent) / interval / 1e3, 2),
    }

    return stats_mem | stats_cpu | stats_disk | stats_net
