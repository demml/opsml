# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum
from typing import Any, Dict, Optional, Protocol, Union, Mapping

import numpy as np
import pyarrow as pa
from pydantic import BaseModel, ConfigDict
import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
from opsml.registry.image import ImageDataset


# DataCard data type hints
class PandasDataFrame(Protocol):
    ...


class PolarsDataFrame(Protocol):
    ...


class DataTypeClass(type):
    ...


class DataType(type):
    ...


class PandasTimestamp(Protocol):
    ...


ValidData = Union[np.ndarray, PandasDataFrame, PolarsDataFrame, pa.Table, ImageDataset]


PolarsDataType: TypeAlias = Union["DataTypeClass", "DataType"]
PolarsSchemaDict: TypeAlias = Mapping[str, PolarsDataType]


def get_class_name(object_: ValidData) -> str:
    """Parses object to get the fully qualified class name.
    Used during type checking to avoid unnecessary imports.

    Args:
        object_:
            object to parse
    Returns:
        fully qualified class name
    """
    klass = object_.__class__
    module = object_.__module
    if module == "builtins":
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + klass.__qualname__


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    ARROW_TABLE = "Table"
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    DICTIONARY = "Dictionary"
    IMAGE_DATASET = "ImageDataset"


class AllowedDataType(str, Enum):
    PANDAS = "pandas.core.frame.DataFrame"
    PYARROW = "pyarrow.lib.Table"
    POLARS = "polars.dataframe.frame.DataFrame"
    NUMPY = "numpy.ndarray"
    IMAGE = "ImageDataset"
    DICT = "dict"


class ArrowTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Dict[str, Any]] = None


class DataTypeChecker:
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_type(data_type: str) -> bool:
        raise NotImplementedError


class PandasTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        import pandas as pd

        assert isinstance(data, pd.DataFrame), "Data must be a pandas dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PANDAS == data_type


class PolarsTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        import polars as pl

        assert isinstance(data, pl.DataFrame), "Data must be a polars dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.POLARS == data_type


class NumpyTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, np.ndarray), "Data must be a numpy array"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.NUMPY == data_type


class PyarrowTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, pa.Table), "Data must be a pyarrow table"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PYARROW == data_type


class ImageTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, ImageDataset), "Data must be an ImageDataset"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.IMAGE in data_type


def check_data_type(data: ValidData) -> str:
    """Checks that the data type is one of the allowed types

    Args:
        data:
            data to check

    Returns:
        data type
    """
    data_type = get_class_name(data)

    data_type_checker = next(
        (
            data_type_checker
            for data_type_checker in DataTypeChecker.__subclasses__()
            if data_type_checker.validate_type(data_type)
        ),
        None,
    )

    if data_type_checker is None:
        raise ValueError(
            f"""Data must be one of the following types: numpy array, pandas dataframe, 
            polars dataframe, pyarrow table, or ImageDataset. Received {data_type}
            """
        )

    data_type_checker.check_data_type(data)

    return data_type
