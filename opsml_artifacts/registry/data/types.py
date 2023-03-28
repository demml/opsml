from enum import Enum
from typing import Dict, Optional, Union

import numpy as np
import pyarrow as pa
from pydantic import BaseModel


class AllowedTableTypes(str, Enum):
    NDARRAY = "ndarray"
    TABLE = "Table"
    DATAFRAME = "DataFrame"


class ArrowTable(BaseModel):
    table: Union[pa.Table, np.ndarray]
    table_type: AllowedTableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Dict[str, Union[str, None]]] = None

    class Config:
        arbitrary_types_allowed = True
