from enum import Enum
from typing import Dict, Optional, Union, Any, Mapping

import numpy as np
import pyarrow as pa
from polars.datatypes.classes import DataType, DataTypeClass
from pydantic import BaseModel, ConfigDict


POLARS_SCHEMA = Mapping[str, Union[DataTypeClass, DataType]]


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    ARROW_TABLE = "Table"
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    DICTIONARY = "Dictionary"


class ArrowTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Union[Dict[str, Any], POLARS_SCHEMA]] = None
