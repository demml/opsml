from opsml.projects._hw_metrics import CPUMetricsLogger, MemoryMetricsLogger, NetworkMetricsLogger, CPUMetrics, MemoryMetrics, NetworkRates


def test_cpu_metrics_logger() -> None:
    cpu_logger = CPUMetricsLogger(15, True, True)
    metrics: CPUMetrics = cpu_logger.get_metrics()
    
    assert isinstance(metrics.cpu_percent_avg, float)
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
    