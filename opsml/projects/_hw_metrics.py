# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import time
import abc
import os
import psutil

from typing import List, Dict, Any
from collections import namedtuple

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class BaseMetricsLogger(abc.ABC):
    """The base class for all system metrics data loggers. It implements common scheduling and error handling."""

    def __init__(
        self,
        initial_interval: float,
        max_failed_attempts: int = 10,
        minimal_interval: float = 10,
    ):
        """
        Args:
            initial_interval (float):
                The initial interval in seconds between logging attempts.
            max_failed_attempts (int):
                The maximum number of failed attempts before the logger stops trying to log data.
            minimal_interval (float):
                The minimal interval in seconds between logging attempts.

        """
        self.interval = _valid_interval(initial_interval, minimal_interval)
        self.max_failed_attempts = max_failed_attempts

        self.last_log_attempt = 0.0
        self.subsequent_failures_counter = 0

        logger.debug(
            "Metrics data logger created: {} with interval: {}",
            self.get_name(),
            initial_interval,
        )

    def log_metric_data(self) -> None:
        """Attempts to log metric data"""
        try:
            metrics = self.get_metrics()
            if _not_empty(metrics) > 0:
                self.callback(metrics)

            # reset failures counter to avoid accumulation of not subsequent failures
            self.subsequent_failures_counter = 0
        except Exception as e:
            logger.error("Failed to log system metrics: {}. Error: {}", self.get_name(), e)
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
    def get_metrics(self) -> Dict[str, float]:
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

    logger.warning(
        "Provided interval is too low, falling back to the minimum interval ({} Seconds)",
        minimal_interval,
    )
    return minimal_interval


def _not_empty(metrics: Dict[str, float]) -> bool:
    """Check if metric dict is not empty"""
    return len(metrics) > 0


## Classes for hardware metrics

## CPU metrics


def family() -> List[int]:
    main_process = psutil.Process(os.getpid())
    children = main_process.children(recursive=True)

    return [main_process.pid] + [child.pid for child in children]


def process_tree() -> float:
    """Process pids"""

    processes_family = [psutil.Process(pid=pid) for pid in family() if psutil.pid_exists(pid)]

    for process in processes_family:
        process.cpu_percent()

    # We need to sleep here in order to get CPU utilization from psutil
    UTILIZATION_MEASURE_INTERVAL = 0.3
    time.sleep(UTILIZATION_MEASURE_INTERVAL)

    result: float = sum([process.cpu_percent() for process in processes_family if process.is_running()])

    return result


class CPUMetricsLogger(BaseMetricsLogger):
    """CPU metrics data logger. It logs CPU utilization and compute metrics."""

    def __init__(
        self,
        initial_interval: float,
        include_cpu_per_core: bool,
        include_compute_metrics: bool,
        **kwargs: Any,
    ):
        """Instantiates a new CPU metrics data logger.

        Args:
            initial_interval (float):
                The initial interval in seconds between logging attempts.
            include_cpu_per_core (bool):
                Whether to include CPU utilization per core.
            include_compute_metrics (bool):
                Whether to include compute metrics.
            **kwargs:
                Additional arguments to pass to the base class.
        """
        super().__init__(initial_interval, **kwargs)
        self.include_compute_metrics = include_compute_metrics
        self.include_cpu_per_core = include_cpu_per_core

    def get_metrics(self) -> Dict[str, float]:
        """Get CPU metrics.

        Returns:
            dict: A dictionary with CPU metrics.
        """

        cpu_metrics = self._cpu_percent_metrics()
        loadavg_metrics = self._loadavg_metrics()

        metrics = {**cpu_metrics, **loadavg_metrics}

        return metrics

    def get_name(self) -> str:
        return "[sys.ram,sys.cpu,sys.load]"

    def available(self) -> bool:
        return psutil is not None

    def _loadavg_metrics(self) -> Dict[str, float]:
        result: Dict[str, float] = {}
        result["sys.load.avg"] = psutil.getloadavg()[0]
        return result

    def _cpu_percent_metrics(self) -> Dict[str, float]:
        """Gets CPU utilization metrics.

        Args:
            include_compute (bool):
                Whether to include compute metrics.
            include_per_core (bool):
                Whether to include CPU utilization per core.
        """
        percents = psutil.cpu_percent(interval=None, percpu=True)

        result = {}
        if len(percents) > 0:
            avg_percent = sum(percents) / len(percents)
            result["sys.cpu.percent.avg"] = avg_percent

            if self.include_compute_metrics:
                result["sys.compute.overall"] = round(avg_percent, 1)
                result["sys.compute.utilized"] = process_tree()

            if self.include_cpu_per_core:
                for i, percent in enumerate(percents):
                    result["sys.cpu.percent.%02d" % (i + 1)] = percent

        return result


## Memory


class MemoryMetricsDataLogger(BaseMetricsLogger):
    def __init__(self, include_swap_memory: bool):
        self.include_swap_memory = include_swap_memory

    def get_metrics(self) -> Dict[str, float]:
        """Get memory metrics.

        Returns:
            dict: A dictionary with memory metrics.
        """
        return self._ram_metrics()

    def _ram_metrics(self) -> Dict[str, float]:
        virtual_memory = psutil.virtual_memory()

        result = {
            "sys.ram.total": virtual_memory.total,
            "sys.ram.used": virtual_memory.total - virtual_memory.available,
            "sys.ram.available": virtual_memory.available,
            "sys.ram.percent.used": virtual_memory.percent,
        }

        if self.include_swap_memory:
            swap_memory = psutil.swap_memory()
            swap_result = {
                "sys.swap.total": swap_memory.total,
                "sys.swap.used": swap_memory.used,
                "sys.swap.free": swap_memory.free,
                "sys.swap.percent": (swap_memory.total - swap_memory.free) / swap_memory.total * 100,
            }

            # combine the two dictionaries
            result = {**result, **swap_result}

        return result


## Network usage

NetworkRatesResult = namedtuple("NetworkRatesResult", ["bytes_sent_rate", "bytes_recv_rate"])


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

        self._save_current_state(time_now=now, bytes_sent=counters.bytes_sent, bytes_recv=counters.bytes_recv)

        return NetworkRatesResult(bytes_recv_rate=int(bytes_recv_rate), bytes_sent_rate=int(bytes_sent_rate))

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
