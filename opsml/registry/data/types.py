# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum
from typing import Any, Dict, Optional, Union, Protocol, runtime_checkable
from functools import wraps
import numpy as np
import pyarrow as pa
from pydantic import BaseModel, ConfigDict
from opsml.registry.image import ImageDataset

# POLARS_SCHEMA = Mapping[str, Union[DataTypeClass, DataType]]  # pylint: disable=invalid-name


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    ARROW_TABLE = "Table"
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    DICTIONARY = "Dictionary"
    IMAGE_DATASET = "ImageDataset"


class AllowedDataType(str, Enum):
    PANDAS = "pandas"
    PYARROW = "pyarrow"
    POLARS = "polars"
    NUMPY = "numpy"


class ArrowTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Dict[str, Any]] = None


@runtime_checkable
class PandasDataFrame(Protocol):
    ...


@runtime_checkable
class PolarsDataFrame(Protocol):
    ...


@runtime_checkable
class NDArray(Protocol):
    ...


@runtime_checkable
class PyarrowTable(Protocol):
    ...


ValidData = Union[NDArray, PandasDataFrame, PolarsDataFrame, PyarrowTable, ImageDataset]


def import_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
                f"""{error}. Please install the required dependencies for the data type you are using."""
            )

    return wrapper


class DataTypeChecker:
    def __init__(self, data: ValidData) -> None:
        self.data = data

    @import_decorator
    def check_data_type(self) -> None:
        raise NotImplementedError

    @staticmethod
    def validate_type(data_type: str) -> bool:
        raise NotImplementedError


class PandasTypeChecker(DataTypeChecker):
    @import_decorator
    def check_data_type(self) -> None:
        import pandas as pd

        assert isinstance(self.data, pd.DataFrame), "Data must be a pandas dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PANDAS in data_type


class PolarsTypeChecker(DataTypeChecker):
    @import_decorator
    def check_data_type(self) -> None:
        import polars as pl

        assert isinstance(self.data, pl.DataFrame), "Data must be a polars dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.POLARS in data_type


class NumpyTypeChecker(DataTypeChecker):
    @import_decorator
    def check_data_type(self) -> None:
        import numpy as np

        assert isinstance(self.data, np.ndarray), "Data must be a numpy array"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.NUMPY in data_type


class PyarrowTypeChecker(DataTypeChecker):
    @import_decorator
    def check_data_type(self) -> None:
        import pyarrow as pa

        assert isinstance(self.data, pa.Table), "Data must be a pyarrow table"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PYARROW in data_type


def check_data_type(data: ValidData) -> None:
    data_type = str(data.__class__)
    """Checks that the data type is one of the allowed types"""

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

    data_type_checker(data=data).check_data_type()
