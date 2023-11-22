# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum
from typing import Any, Dict, Mapping, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from polars.datatypes.classes import DataType, DataTypeClass
from pydantic import BaseModel, ConfigDict

from opsml.registry.image import ImageDataset

POLARS_SCHEMA = Mapping[str, Union[DataTypeClass, DataType]]  # pylint: disable=invalid-name

ValidData = Union[np.ndarray, pd.DataFrame, pl.DataFrame, pa.Table, ImageDataset]


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
    IMAGE = "ImageDataset"


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
        assert isinstance(data, pd.DataFrame), "Data must be a pandas dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PANDAS in data_type


class PolarsTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, pl.DataFrame), "Data must be a polars dataframe"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.POLARS in data_type


class NumpyTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, np.ndarray), "Data must be a numpy array"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.NUMPY in data_type


class PyarrowTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, pa.Table), "Data must be a pyarrow table"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.PYARROW in data_type


class ImageTypeChecker(DataTypeChecker):
    @staticmethod
    def check_data_type(data: ValidData) -> None:
        assert isinstance(data, ImageDataset), "Data must be an ImageDataset"

    @staticmethod
    def validate_type(data_type: str) -> bool:
        return AllowedDataType.IMAGE in data_type


def check_data_type(data: ValidData) -> None:
    """Checks that the data type is one of the allowed types"""
    data_type = str(data.__class__)

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
