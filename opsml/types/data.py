# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum
from typing import Dict, Optional, Union

from pydantic import BaseModel

from opsml.types.extra import Description
from opsml.types.model import Feature


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
    TORCH_DATASET = "torch.utils.data.Dataset"
    TENSORFLOW_TENSOR = "tensorflow.python.framework.ops.EagerTensor"
    TUPLE = "tuple"
    LIST = "list"
    STR = "str"
    ORDERED_DICT = "collections.OrderedDict"
    JOBLIB = "joblib"


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

    interface_type: str = ""
    data_type: str = ""
    description: Description = Description()
    feature_map: Dict[str, Feature] = {}
    additional_info: Dict[str, Union[float, int, str]] = {}
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None
