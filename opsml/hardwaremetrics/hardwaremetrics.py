# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

## Import section
import time
import abc
import logging
import os
import concurrent.futures

try:
    import psutil
except Exception:
    psutil = None

from typing import Any, List
from collections import namedtuple
#from opsml.projects.active_run import ActiveRun

LOGGER = logging.getLogger(__name__)


class BaseMetricsDataLogger(abc.ABC):
    """The base class for all system metrics data loggers. It implements common scheduling and error handling."""

    def __init__(
        self,
        initial_interval: float,
        max_failed_attempts: int = 10,
        minimal_interval: float = 10,
    ):
        self.interval = _valid_interval(initial_interval, minimal_interval)
        self.max_failed_attempts = max_failed_attempts

        self.last_log_attempt = 0.0
        self.subsequent_failures_counter = 0

        LOGGER.debug(
            "Metrics data logger created: %s with interval: %.1f",
            self.get_name(),
            initial_interval,
        )

    def log_metric_data(self):
        try:
            metrics = self.get_metrics()
            if _not_empty(metrics) > 0:
                self.callback(metrics)

            # reset failures counter to avoid accumulation of not subsequent failures
            self.subsequent_failures_counter = 0
        except Exception:
            LOGGER.warning(
                "Failed to log system metrics: %s", self.get_name(), exc_info=True
            )
            self.subsequent_failures_counter += 1

        self.last_log_attempt = time.time()

    def should_log_data(self) -> bool:
        if self.failed() or not self.available():
            return False

        # check interval
        next_run = self.last_log_attempt + self.interval  # seconds
        now = time.time()
        result = next_run <= now
        return result

    def failed(self) -> bool:
        return self.subsequent_failures_counter >= self.max_failed_attempts

    @abc.abstractmethod
    def get_metrics(self):
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def available(self) -> bool:
        pass


def _valid_interval(interval: float, minimal_interval: float) -> float:
    if interval >= minimal_interval:
        return interval

    LOGGER.warning(
        "Provided interval is too low, falling back to the minimum interval (%.1f Seconds)",
        minimal_interval,
    )
    return minimal_interval


def _not_empty(metrics: Any):
    if metrics is None:
        return False

    if hasattr(metrics, "__len__") or hasattr(metrics, "len"):
        return len(metrics) > 0

    return True

## Classes for hardware metrics

## CPU metrics

def family() -> List[int]:
    main_process = psutil.Process(os.getpid())
    children = main_process.children(recursive=True)

    return [main_process.pid] + [child.pid for child in children]

def process_tree():
    if psutil is None:
        return

    processes_family = [
        psutil.Process(pid=pid) for pid in family() if psutil.pid_exists(pid)
    ]
    for process in processes_family:
        process.cpu_percent()

    # We need to sleep here in order to get CPU utilization from psutil
    UTILIZATION_MEASURE_INTERVAL = 0.3
    time.sleep(UTILIZATION_MEASURE_INTERVAL)

    result = sum(
        [process.cpu_percent() for process in processes_family if process.is_running()]
    )

    return result

class CPUMetricsDataLogger(BaseMetricsDataLogger):
    def __init__(
        self,
        initial_interval: float,
        include_cpu_per_core: bool,
        include_compute_metrics: bool,
        **kwargs
    ):
        super().__init__(initial_interval, **kwargs)
        self.include_compute_metrics = include_compute_metrics
        self._include_cpu_per_core = include_cpu_per_core

    def get_metrics(self):
        cpu_metrics = _cpu_percent_metrics(
            self.include_compute_metrics, self._include_cpu_per_core
        )
        #ram_metrics = _ram_metrics()
        loadavg_metrics = _loadavg_metrics()

        metrics = {**cpu_metrics, **loadavg_metrics}

        return metrics

    def get_name(self) -> str:
        return "[sys.ram,sys.cpu,sys.load]"

    def available(self) -> bool:
        return psutil is not None


def _cpu_percent_metrics(include_compute, include_per_core):
    percents = psutil.cpu_percent(interval=None, percpu=True)

    result = {}
    if len(percents) > 0:
        avg_percent = sum(percents) / len(percents)
        result["sys.cpu.percent.avg"] = avg_percent

        if include_compute:
            result["sys.compute.overall"] = round(avg_percent, 1)
            result["sys.compute.utilized"] = process_tree()

        if include_per_core:
            for (i, percent) in enumerate(percents):
                result["sys.cpu.percent.%02d" % (i + 1)] = percent

    return result


def _loadavg_metrics():
    result = {}

    try:
        # psutil <= 5.6.2 did not have getloadavg:
        if hasattr(psutil, "getloadavg"):
            result["sys.load.avg"] = psutil.getloadavg()[0]
        else:
            # Do not log an empty metric
            pass
    except OSError:
        result["sys.load.avg"] = None

    return result


## Memory

## Potentially use asyncio class asyncio.TaskGroup to handle all hardware metric calls and send them to db once all are finished

class MemoryMetricsDataLogger(BaseMetricsDataLogger):
    
    def __init__(
    self,
    include_swap_memory: bool,
    ):
        
        self.include_swap_memory = include_swap_memory
    
    def get_metrics(include_swap_memory=False):
        ram_metrics, swap_result = _ram_metrics(
        )

        if include_swap_memory==True:
            return ram_metrics, swap_result
        return ram_metrics


def _ram_metrics():
    virtual_memory = psutil.virtual_memory()
    swap_memory = psutil.swap_memory()

    result = {
        "sys.ram.total": virtual_memory.total,
        "sys.ram.used": virtual_memory.total - virtual_memory.available,
        "sys.ram.available": virtual_memory.available,
        "sys.ram.percent.used": virtual_memory.percent,
    }

    swap_result = {
        "sys.swap.total": swap_memory.total,
        "sys.swap.used": swap_memory.used,
        "sys.swap.free": swap_memory.free,
        "sys.swap.percent": (swap_memory.total - swap_memory.free) / swap_memory.total * 100,
    }

    return result, swap_result


## Network usage

NetworkRatesResult = namedtuple(
    "NetworkRatesResult", ["bytes_sent_rate", "bytes_recv_rate"]
)

class NetworkRatesProbe(object):
    def __init__(self):
        self.last_tick = 0.0
        self.last_bytes_recv = 0
        self.last_bytes_sent = 0

    def current_rate(self):
        if psutil is None:
            return None

        counters = psutil.net_io_counters()
        now = time.time()
        if self.last_tick == 0.0:
            self._save_current_state(
                time_now=now,
                bytes_sent=counters.bytes_sent,
                bytes_recv=counters.bytes_recv,
            )
            return None

        elapsed = now - self.last_tick
        bytes_sent_rate = (counters.bytes_sent - self.last_bytes_sent) / elapsed
        bytes_recv_rate = (counters.bytes_recv - self.last_bytes_recv) / elapsed

        self._save_current_state(
            time_now=now, bytes_sent=counters.bytes_sent, bytes_recv=counters.bytes_recv
        )

        return NetworkRatesResult(
            bytes_recv_rate=int(bytes_recv_rate), bytes_sent_rate=int(bytes_sent_rate)
        )

    def _save_current_state(self, time_now: float, bytes_sent: int, bytes_recv: int):
        self.last_tick = time_now
        self.last_bytes_recv = bytes_recv
        self.last_bytes_sent = bytes_sent


class NetworkMetricsDataLogger(BaseMetricsDataLogger):
    def __init__(
        self,
        initial_interval: float,
    ):
        super().__init__(initial_interval)
        self.network_rates_probe = NetworkRatesProbe()

    def get_metrics(self):
        result = self.network_rates_probe.current_rate()
        if result is None:
            return {}
        metrics = {
            "sys.network.send_bps": result.bytes_sent_rate,
            "sys.network.receive_bps": result.bytes_recv_rate,
        }
        return metrics

    def get_name(self) -> str:
        return "[sys.network]"

    def available(self) -> bool:
        return psutil is not None


# metrics = MemoryMetricsDataLogger.get_metrics(include_swap_memory=False)
# n_metrics = NetworkMetricsDataLogger(initial_interval=10).get_metrics()
# cpu_metrics = CPUMetricsDataLogger(initial_interval=3, include_compute_metrics=True, include_cpu_per_core=True).get_metrics()

# def get_hwmetrics():
#     while ActiveRun.active() == True:

#         format = "%(asctime)s: %(message)s"
#         logging.basicConfig(format=format, level=logging.INFO,
#                             datefmt="%H:%M:%S")

#         with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#             executor.map(print(MemoryMetricsDataLogger.get_metrics(include_swap_memory=False)))
#             executor.map(print(NetworkMetricsDataLogger(initial_interval=10).get_metrics()))
#             executor.map(print(CPUMetricsDataLogger(initial_interval=10, include_compute_metrics=True, include_cpu_per_core=True).get_metrics()))
#         time.sleep(15)
