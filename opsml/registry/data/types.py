from enum import Enum
from typing import Dict, Optional, Union

import numpy as np
import pyarrow as pa
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
    feature_map: Optional[Dict[str, Union[str, None]]] = None

    class Config:
        arbitrary_types_allowed = True
