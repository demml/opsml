import platform
from typing import Any, Dict, List, Optional, cast

import psutil
from pydantic import BaseModel, model_validator
from pynvml import (
    NVMLError,
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetName,
    nvmlInit,
)


class CPUMetrics(BaseModel):
    """CPU metrics data model."""

    cpu_percent_utilization: float = 0.0
    cpu_percent_per_core: Optional[List[float]] = None
    compute_overall: Optional[float] = None
    compute_utilized: Optional[float] = None
    load_avg: float


class GPUMetrics(BaseModel):
    """GPU metrics data model."""

    gpu_percent_utilization: float = 0.0
    gpu_percent_per_core: Optional[List[float]] = None


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
    gpu: Optional[GPUMetrics] = None


class GPUDeviceInfo(BaseModel):
    total: int
    used: int


class NVMLHandler:
    """Helper for nvml library"""

    @staticmethod
    def init_nvml() -> None:
        nvmlInit()

    @staticmethod
    def get_device_handle(index: int) -> Any:
        return nvmlDeviceGetHandleByIndex(index)

    @staticmethod
    def get_device_info(handle: Any) -> GPUDeviceInfo:
        info = nvmlDeviceGetMemoryInfo(handle)

        return GPUDeviceInfo(total=info.total, used=info.used)

    @staticmethod
    def get_device_count() -> int:
        return cast(int, nvmlDeviceGetCount())

    @staticmethod
    def get_device_name(handle: Any) -> str:
        return cast(str, nvmlDeviceGetName(handle))


class ComputeEnvironment(BaseModel):
    cpu_count: int = psutil.cpu_count(logical=False)
    memory: int = psutil.virtual_memory().total
    disk_space: int = psutil.disk_usage("/").total
    system: str = platform.system()
    release: str = platform.release()
    architecture_bits: str = platform.architecture()[0]
    python_version: str = platform.python_version()
    python_compiler: str = platform.python_compiler()
    gpu_count: int = 0
    gpu_devices: List[str] = []
    gpu_device_memory: Dict[str, float] = {}

    @model_validator(mode="before")
    @classmethod
    def _check_for_gpu(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        try:
            NVMLHandler.init_nvml()
            gpu_devices = []
            gpu_memory = {}
            device_count = NVMLHandler.get_device_count()

            for i in range(device_count):
                handle = NVMLHandler.get_device_handle(i)
                device_name = NVMLHandler.get_device_name(handle)
                device_memory = NVMLHandler.get_device_info(handle).total

                gpu_devices.append(device_name)
                gpu_memory[device_name] = device_memory

            values["gpu_count"] = device_count
            values["gpu_devices"] = gpu_devices
            values["gpu_device_memory"] = gpu_memory

        except NVMLError as _:
            pass

        return values
