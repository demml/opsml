# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from pydantic import BaseModel, ConfigDict, field_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.types.extra import Description

ValidData = Union[np.ndarray, pd.DataFrame, pl.DataFrame, pa.Table, ImageDataset]  # type: ignore


# need for old v1 compat
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
    SQL = "sql"
    PROFILE = "profile"
    TRANSFORMER_BATCH = "transformers.tokenization_utils_base.BatchEncoding"
    STRING = "str"
    TORCH_TENSOR = "torch.Tensor"
    TENSORFLOW_TENSOR = "tensorflow.python.framework.ops.EagerTensor"
    TUPLE = "tuple"
    LIST = "list"
    STR = "str"


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
    class_name = get_class_name(data)

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
    if isinstance(data, str):
        return AllowedDataType.STRING.value
    if class_name == AllowedDataType.TRANSFORMER_BATCH.value:
        return AllowedDataType.TRANSFORMER_BATCH.value
    if class_name == AllowedDataType.TORCH_TENSOR.value:
        return AllowedDataType.TORCH_TENSOR.value
    if class_name == AllowedDataType.TENSORFLOW_TENSOR.value:
        return AllowedDataType.TENSORFLOW_TENSOR.value

    raise ValueError(
        f"""Data must be one of the following types: numpy array, pandas dataframe, 
        polars dataframe, pyarrow table, or ImageDataset. Received {str(type(data))}
        """
    )


@dataclass
class DataCardUris:
    """Data uri holder for DataCardMetadata

    Args:
        data_uri:
            Location where converted data is stored
        datacard_uri:
            Location where DataCard is stored
        profile_uri:
            Location where profile is stored
        profile_html_uri:
            Location where profile html is stored
    """

    data_uri: Optional[str] = None
    datacard_uri: Optional[str] = None
    profile_uri: Optional[str] = None
    profile_html_uri: Optional[str] = None


class DataCardMetadata(BaseModel):

    """Create a DataCard metadata

    Args:
        description:
            Description for your data
        feature_map:
            Map of features in data (inferred when converting to pyarrow table)
        feature_descriptions:
            Dictionary of features and their descriptions
        additional_info:
            Dictionary of additional info to associate with data
            (i.e. if data is tokenized dataset, metadata could be {"vocab_size": 200})
        data_uri:
            Location where converted pyarrow table is stored
        runcard_uid:
            Id of RunCard that created the DataCard
        pipelinecard_uid:
            Associated PipelineCard
        uris:
            DataCardUris object containing all uris associated with DataCard
    """

    description: Description = Description()
    feature_map: Optional[Dict[str, Optional[Any]]] = None
    data_type: str = "undefined"
    feature_descriptions: Dict[str, str] = {}
    additional_info: Dict[str, Union[float, int, str]] = {}
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None
    uris: DataCardUris = DataCardUris()

    @field_validator("feature_descriptions", mode="before")
    @classmethod
    def lower_descriptions(cls, feature_descriptions: Dict[str, str]) -> Dict[str, str]:
        if not bool(feature_descriptions):
            return feature_descriptions

        feat_dict = {}
        for feature, description in feature_descriptions.items():
            feat_dict[feature.lower()] = description.lower()

        return feat_dict
