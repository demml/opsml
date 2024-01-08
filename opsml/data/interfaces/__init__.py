from opsml.data.interfaces._arrow import ArrowData
from opsml.data.interfaces._base import DataInterface
from opsml.data.interfaces._numpy import NumpyData
from opsml.data.interfaces._pandas import PandasData
from opsml.data.interfaces._polars import PolarsData
from opsml.data.interfaces._sql import SqlData
from opsml.data.interfaces._torch import TorchData
from opsml.helpers.utils import all_subclasses


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
