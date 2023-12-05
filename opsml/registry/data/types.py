# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from pydantic import BaseModel, ConfigDict

from opsml.registry.image.dataset import ImageDataset

ValidData = Union[np.ndarray, pd.DataFrame, pl.DataFrame, pa.Table, ImageDataset]  # type: ignore


def get_class_name(object_: object) -> str:
    """Parses object to get the fully qualified class name.
    Used during type checking to avoid unnecessary imports.

    Args:
        object_:
            object to parse
    Returns:
        fully qualified class name
    """
    klass = object_.__class__
    module = klass.__module__
    if module == "builtins":
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + klass.__qualname__


class AllowedDataType(str, Enum):
    PANDAS = "pandas.core.frame.DataFrame"
    PYARROW = "pyarrow.lib.Table"
    POLARS = "polars.dataframe.frame.DataFrame"
    NUMPY = "numpy.ndarray"
    IMAGE = "ImageDataset"
    DICT = "dict"
    SQL = "sql"


class ArrowTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table: Union[pa.Table, np.ndarray]  # type: ignore
    storage_uri: Optional[str] = None
    feature_map: Optional[Dict[str, Any]] = None


def check_data_type(data: ValidData) -> str:
    """Checks that the data type is one of the allowed types

    Args:
        data:
            data to check

    Returns:
        data type
    """
    if isinstance(data, dict):
        return AllowedDataType.DICT.value
    if isinstance(data, ImageDataset):
        return AllowedDataType.IMAGE.value
    if isinstance(data, np.ndarray):
        return AllowedDataType.NUMPY.value
    if isinstance(data, pd.DataFrame):
        return AllowedDataType.PANDAS.value
    if isinstance(data, pl.DataFrame):
        return AllowedDataType.POLARS.value
    if isinstance(data, pa.Table):
        return AllowedDataType.PYARROW.value

    raise ValueError(
        f"""Data must be one of the following types: numpy array, pandas dataframe, 
        polars dataframe, pyarrow table, or ImageDataset. Received {str(type(data))}
        """
    )
