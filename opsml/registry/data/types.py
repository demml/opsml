# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union, Any, Mapping

import numpy as np
import pyarrow as pa
from polars.datatypes.classes import DataType, DataTypeClass
from pydantic import BaseModel, ConfigDict, field_validator


POLARS_SCHEMA = Mapping[str, Union[DataTypeClass, DataType]]  # pylint: disable=invalid-name


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


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    ARROW_TABLE = "Table"
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    DICTIONARY = "Dictionary"
    IMAGE_DATASET = "ImageDataset"


class ArrowTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Union[Dict[str, Any], POLARS_SCHEMA]] = None


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

    description: Optional[str] = None
    feature_map: Optional[Dict[str, Optional[Any]]] = None
    data_type: Optional[str] = None
    feature_descriptions: Dict[str, str] = {}
    additional_info: Dict[str, Union[float, int, str]] = {}
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    uris: DataCardUris = DataCardUris()

    @field_validator("feature_descriptions", mode="before")
    def lower_descriptions(cls, feature_descriptions):
        if not bool(feature_descriptions):
            return feature_descriptions

        feat_dict = {}
        for feature, description in feature_descriptions.items():
            feat_dict[feature.lower()] = description.lower()
            return feat_dict
