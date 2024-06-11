from typing import List, Optional

from pydantic import BaseModel


class CPUMetrics(BaseModel):
    """CPU metrics data model."""

    cpu_percent_avg: float = 0.0
    cpu_percent_per_core: Optional[List[float]] = None
    compute_overall: Optional[float] = None
    compute_utilized: Optional[float] = None
    load_avg: float


class MemoryMetrics(BaseModel):
    """Memory metrics data model."""

    sys_ram_total: int = 0
    sys_ram_used: int = 0
    sys_ram_available: int = 0
    sys_ram_percent_used: float = 0.0
    sys_swap_total: Optional[int] = None
    sys_swap_used: Optional[int] = None
    sys_swap_free: Optional[int] = None
    sys_swap_percent: Optional[float] = None


class NetworkRates(BaseModel):
    """Network rates data model."""

    bytes_recv: float = 0.0
    bytes_sent: float = 0.0


class HardwareMetrics(BaseModel):
    cpu: CPUMetrics
    memory: MemoryMetrics
    network: NetworkRates
