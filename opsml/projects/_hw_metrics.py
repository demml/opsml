# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import abc
import os
import time
from typing import Any, Dict, List

import psutil

from opsml.helpers.logging import ArtifactLogger
from opsml.types import CPUMetrics, HardwareMetrics, MemoryMetrics, NetworkRates

logger = ArtifactLogger.get_logger()

_UTILIZATION_MEASURE_INTERVAL = 0.3


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

        logger.debug("Metrics data logger created: {} with interval: {}", self.name, initial_interval)

    # def log_metric_data(self) -> bool:
    #    """Attempts to log metric data"""
    #    try:
    #        metrics = self.get_metrics()
    #        if _not_empty(metrics) > 0:
    #            self.callback(metrics)
    #
    #        # reset failures counter to avoid accumulation of not subsequent failures
    #        self.subsequent_failures_counter = 0
    #    except Exception as e:  # pylint: disable=broad-except
    #        logger.error("Failed to log system metrics: {}. Error: {}", self.get_name(), e)
    #        self.subsequent_failures_counter += 1
    #
    #    self.last_log_attempt = time.time()
    #
    #    # check interval
    #    next_run = self.last_log_attempt + self.interval  # seconds
    #    now = time.time()
    #    result = next_run <= now
    #
    #    return result

    def failed(self) -> bool:
        return self.subsequent_failures_counter >= self.max_failed_attempts

    @abc.abstractmethod
    def get_metrics(self) -> Any:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
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


class CPUMetricsLogger(BaseMetricsLogger):
    """CPU metrics data logger. It logs CPU utilization and compute metrics."""

    def __init__(
        self,
        initial_interval: float,
        include_cpu_per_core: bool,
        include_compute_metrics: bool,
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
        super().__init__(initial_interval)
        self.include_compute_metrics = include_compute_metrics
        self.include_cpu_per_core = include_cpu_per_core

    def get_metrics(self) -> CPUMetrics:
        """Get CPU metrics.

        Returns:
            dict: A dictionary with CPU metrics.
        """

        cpu_metrics = self._cpu_percent_metrics()
        cpu_metrics["load_avg"] = psutil.getloadavg()[0]

        return CPUMetrics(**cpu_metrics)

    @property
    def name(self) -> str:
        return "[sys.cpu]"

    def family(self) -> List[int]:
        main_process = psutil.Process(os.getpid())
        children = main_process.children(recursive=True)

        return [main_process.pid] + [child.pid for child in children]

    def process_tree(self) -> float:
        """Process pids"""

        processes_family = [psutil.Process(pid=pid) for pid in self.family() if psutil.pid_exists(pid)]

        for process in processes_family:
            process.cpu_percent()

        # We need to sleep here in order to get CPU utilization from psutil

        time.sleep(_UTILIZATION_MEASURE_INTERVAL)

        result: float = sum(process.cpu_percent() for process in processes_family if process.is_running())

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
            result["cpu_percent_avg"] = avg_percent

            if self.include_compute_metrics:
                result["compute_overall"] = round(avg_percent, 1)
                result["compute_utilized"] = self.process_tree()

            if self.include_cpu_per_core:
                result["cpu_percent_per_core"] = list(percents)

        return result


## Memory
class MemoryMetricsLogger(BaseMetricsLogger):
    def __init__(self, initial_interval: float, include_swap_memory: bool):
        """Record memory metrics.

        Args:
            include_swap_memory (bool):
                Whether to include swap memory metrics.
            initial_interval (float):
                The initial interval in seconds between logging attempts.
        """
        self.include_swap_memory = include_swap_memory
        super().__init__(initial_interval)

    def get_metrics(self) -> MemoryMetrics:
        """Get memory metrics.

        Returns:
            dict: A dictionary with memory metrics.
        """
        return self._ram_metrics()

    def _ram_metrics(self) -> MemoryMetrics:
        virtual_memory = psutil.virtual_memory()

        metrics = MemoryMetrics(
            sys_ram_total=virtual_memory.total,
            sys_ram_used=virtual_memory.total - virtual_memory.available,
            sys_ram_available=virtual_memory.available,
            sys_ram_percent_used=virtual_memory.percent,
        )

        if self.include_swap_memory:
            swap_memory = psutil.swap_memory()
            metrics.sys_swap_total = swap_memory.total
            metrics.sys_swap_used = swap_memory.used
            metrics.sys_swap_free = swap_memory.free

            if swap_memory.total > 0:
                metrics.sys_swap_percent = (swap_memory.total - swap_memory.free) / swap_memory.total * 100
            else:
                metrics.sys_swap_percent = 0.0

        return metrics

    @property
    def name(self) -> str:
        return "[sys.ram]"


## Network usage
class NetworkMetricsLogger(BaseMetricsLogger):
    """Network rates probe for record received and sent bytes rates."""

    def __init__(self, initial_interval: float) -> None:
        """Instantiates a new network rates probe.

        Args:
            initial_interval (float):
                The initial interval in seconds between logging attempts.
        """
        self.last_tick = 0.0
        self.last_bytes_recv = 0
        self.last_bytes_sent = 0

        _current_counters = self.counters()
        self._save_current_state(
            time_now=time.time(),
            bytes_sent=_current_counters.bytes_sent,
            bytes_recv=_current_counters.bytes_recv,
        )

        super().__init__(initial_interval)

    def counters(self) -> psutil._common.snetio:
        return psutil.net_io_counters()

    def current_rate(self) -> NetworkRates:
        counters = self.counters()
        now = time.time()

        elapsed = now - self.last_tick

        if elapsed == 0:
            logger.warning("Elapsed time is zero, setting it to 1")
            bytes_sent_rate = 0
            bytes_recv_rate = 0

        else:
            bytes_sent_rate = (counters.bytes_sent - self.last_bytes_sent) / elapsed
            bytes_recv_rate = (counters.bytes_recv - self.last_bytes_recv) / elapsed

        self._save_current_state(
            time_now=now,
            bytes_sent=bytes_sent_rate,
            bytes_recv=bytes_recv_rate,
        )

        return NetworkRates(
            bytes_recv=bytes_recv_rate,
            bytes_sent=bytes_sent_rate,
        )

    def _save_current_state(self, time_now: float, bytes_sent: int, bytes_recv: int) -> None:
        self.last_tick = time_now
        self.last_bytes_sent = bytes_sent
        self.last_bytes_recv = bytes_recv

    def get_metrics(self) -> NetworkRates:
        return self.current_rate()

    @property
    def name(self) -> str:
        return "[sys.network]"


class HardwareMetricsLogger:
    def __init__(self, interval: float = 15):
        self.cpu_logger = CPUMetricsLogger(interval, True, True)
        self.memory_logger = MemoryMetricsLogger(interval, False)
        self.network_logger = NetworkMetricsLogger(interval)

    def get_metrics(self) -> HardwareMetrics:
        metrics = HardwareMetrics(
            cpu=self.cpu_logger.get_metrics(),
            memory=self.memory_logger.get_metrics(),
            network=self.network_logger.get_metrics(),
        )

        return metrics
