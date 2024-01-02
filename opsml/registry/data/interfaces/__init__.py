from opsml.helpers.utils import FileUtils, all_subclasses
from opsml.registry.data.interfaces._arrow import ArrowData
from opsml.registry.data.interfaces._base import DataInterface
from opsml.registry.data.interfaces._numpy import NumpyData
from opsml.registry.data.interfaces._pandas import PandasData
from opsml.registry.data.interfaces._polars import PolarsData
from opsml.registry.data.interfaces._sql import SqlData


def get_data_interface(interface_type: str) -> DataInterface:
    """Load model interface from pathlib object

    Args:
        interface_type:
            Name of interface
    """
    return next(
        (cls for cls in all_subclasses(DataInterface) if cls.name() == interface_type),
        DataInterface,
    )
