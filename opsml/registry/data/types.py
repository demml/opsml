# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
from enum import Enum
from typing import Any, Dict, Optional, Union

import numpy as np
import pyarrow as pa
import pandas as pd
import polars as pl
from pydantic import BaseModel, ConfigDict

from opsml.registry.image import ImageDataset

ValidData = Union[np.ndarray, pd.DataFrame, pl.DataFrame, pa.Table, ImageDataset]


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
        return AllowedDataType.DICT
    if isinstance(data, ImageDataset):
        return AllowedDataType.IMAGE
    if isinstance(data, np.ndarray):
        return AllowedDataType.NUMPY
    if isinstance(data, pd.DataFrame):
        return AllowedDataType.PANDAS
    if isinstance(data, pl.DataFrame):
        return AllowedDataType.POLARS

    raise ValueError(
        f"""Data must be one of the following types: numpy array, pandas dataframe, 
        polars dataframe, pyarrow table, or ImageDataset. Received {str(type(data))}
        """
    )
