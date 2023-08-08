from enum import Enum
from typing import Dict, Optional, Union, Any

import numpy as np
import pyarrow as pa
import polars as pl
from pydantic import BaseModel


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    ARROW_TABLE = "Table"
    PANDAS_DATAFRAME = "PandasDataFrame"
    POLARS_DATAFRAME = "PolarsDataFrame"
    DICTIONARY = "Dictionary"


class ArrowTable(BaseModel):
    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    schema_uri: Optional[str] = None
    feature_map: Optional[Union[Dict[str, Any], pl.type_aliases.SchemaDict]] = None

    class Config:
        arbitrary_types_allowed = True
