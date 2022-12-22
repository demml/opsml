from typing import Union, Optional
import pyarrow as pa
from pydantic import BaseModel
from typing import Dict
from enum import Enum
import numpy as np
from opsml_data.helpers.defaults import params
import datetime
import time
import uuid


class DataArtifacts(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None


class DataStoragePath(BaseModel):
    gcs_uri: str


class TableTypes(str, Enum):
    ndarray = "ndarray"
    Table = "Table"
    DataFrame = "DataFrame"


class ArrowTable(BaseModel):
    table: Union[pa.Table, np.ndarray]
    table_type: TableTypes
    storage_uri: Optional[str] = None
    feature_map: Optional[Dict[str, str]]

    class Config:
        arbitrary_types_allowed = True


class RegisterMetadata(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None
    version: int
    data_type: str
    data_name: str
    team: str
    feature_map: Dict[str, str]
    user_email: str
