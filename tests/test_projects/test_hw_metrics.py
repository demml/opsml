from opsml.projects._hw_metrics import (
    CPUMetrics,
    CPUMetricsLogger,
    GPUMetricsLogger,
    HardwareMetricsLogger,
    MemoryMetrics,
    MemoryMetricsLogger,
    NetworkMetricsLogger,
    NetworkRates,
)
from opsml.types import ComputeEnvironment, NVMLHandler


def test_cpu_metrics_logger() -> None:
    cpu_logger = CPUMetricsLogger(15, True, True)
    metrics: CPUMetrics = cpu_logger.get_metrics()

    assert isinstance(metrics.cpu_percent_utilization, float)
    assert isinstance(metrics.cpu_percent_per_core, list)
    assert isinstance(metrics.cpu_percent_per_core[0], float)
    assert isinstance(metrics.compute_overall, float)
    assert isinstance(metrics.compute_utilized, float)
    assert isinstance(metrics.load_avg, float)


def test_memory_metrics_logger() -> None:
    memory_logger = MemoryMetricsLogger(15, True)
    metrics: MemoryMetrics = memory_logger.get_metrics()

    assert isinstance(metrics.sys_ram_total, int)
    assert isinstance(metrics.sys_ram_used, int)
    assert isinstance(metrics.sys_ram_available, int)
    assert isinstance(metrics.sys_ram_percent_used, float)
    assert isinstance(metrics.sys_swap_total, int)
    assert isinstance(metrics.sys_swap_used, int)
    assert isinstance(metrics.sys_swap_free, int)
    assert isinstance(metrics.sys_swap_percent, float)


def test_network_metrics_logger() -> None:
    network_logger = NetworkMetricsLogger(15)
    metrics: NetworkRates = network_logger.get_metrics()

    assert isinstance(metrics.bytes_sent, float)
    assert isinstance(metrics.bytes_recv, float)


def test_mock_nvm(mock_nvm_handler: NVMLHandler) -> None:
    logger = GPUMetricsLogger(initial_interval=15, gpu_count=2, gpu_devices=["0", "1"])
    assert logger.gpu_count == 2

    metrics = logger.get_metrics()
    assert metrics is not None
    assert metrics.gpu_percent_utilization == 50.0
    assert metrics.gpu_percent_per_core == [50.0, 50.0]


def test_hardware_metrics(mock_nvm_handler: NVMLHandler) -> None:
    env = ComputeEnvironment()
    env.gpu_count = 2
    env.gpu_devices = ["0", "1"]
    assert env.gpu_count == 2
    metric_logger = HardwareMetricsLogger(env, 15)

    metrics = metric_logger.get_metrics()

    assert metrics.cpu.cpu_percent_utilization > 0
    assert metrics.memory.sys_ram_total > 0
    assert metrics.gpu is not None
    assert metrics.gpu.gpu_percent_utilization == 50.0
    assert metrics.gpu.gpu_percent_per_core == [50.0, 50.0]
