from opsml.data.interfaces._arrow import ArrowData
from opsml.data.interfaces._base import DataInterface
from opsml.data.interfaces._image import ImageDataset
from opsml.data.interfaces._numpy import NumpyData
from opsml.data.interfaces._pandas import PandasData
from opsml.data.interfaces._polars import PolarsData
from opsml.data.interfaces._sql import SqlData
from opsml.data.interfaces._text import TextDataset
from opsml.data.interfaces._torch import TorchData
from opsml.data.interfaces.custom_data.base import Dataset
from opsml.data.interfaces.custom_data.text import TextMetadata, TextRecord
from opsml.data.splitter import DataSplit

try:
    from opsml.data.interfaces.custom_data.image import BBox, ImageMetadata, ImageRecord

    extra_imports = ["ImageMetadata", "ImageRecord", "BBox"]

except ModuleNotFoundError:
    extra_imports = []

__all__ = [
    "ArrowData",
    "NumpyData",
    "PandasData",
    "PolarsData",
    "SqlData",
    "TorchData",
    "DataInterface",
    "DataSplit",
    "ImageDataset",
    "TextDataset",
    "TextMetadata",
    "TextRecord",
    "Dataset",
    *extra_imports,
]
