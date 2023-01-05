from enum import Enum
from typing import Dict, List, Optional, Union, cast, Any

import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic import BaseModel, Extra, root_validator


class DataStoragePath(BaseModel):
    gcs_uri: str


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


class RegistryRecord(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None
    data_splits: Optional[Dict[str, List[Dict[str, Any]]]] = None
    version: int
    data_type: str
    data_name: str
    team: str
    feature_map: Dict[str, str]
    user_email: str
    uid: Optional[str] = None

    @root_validator(pre=True)
    def set_attributes(cls, values):  # pylint: disable=no-self-argument
        """Pre checks"""

        if bool(values["data_splits"]):
            values["data_splits"] = {"splits": values["data_splits"]}

        return values
