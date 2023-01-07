from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pyarrow as pa
import pandas as pd
from pydantic import BaseModel, validator, root_validator

from opsml_data.registry.storage import load_record_data_from_storage
from opsml_data.drift.models import DriftReport


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
    dependent_vars: Optional[List[str]] = None

    @validator("data_splits", pre=True)
    def convert_to_dict(cls, splits):  # pylint: disable=no-self-argument
        if bool(splits):
            return {"splits": splits}

        return splits


class LoadedRecord(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None
    data_splits: Optional[List[Dict[str, Any]]] = None
    version: int
    data_type: str
    data_name: str
    team: str
    feature_map: Dict[str, str]
    user_email: str
    uid: Optional[str] = None
    dependent_vars: Optional[List[str]] = None
    data: Union[np.ndarray, pd.DataFrame, pa.Table]
    drift_report: Optional[Dict[str, DriftReport]] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def load_attributes(cls, values):
        values["data_splits"] = LoadedRecord.get_splits(splits=values["data_splits"])
        values["data"] = LoadedRecord.load_data(values=values)
        values["drift_report"] = LoadedRecord.load_drift_report(values=values)

        return values

    @staticmethod
    def get_splits(splits):  # pylint: disable=no-self-argument
        if bool(splits):
            return splits.get("splits")
        return splits

    @staticmethod
    def load_data(values):

        return load_record_data_from_storage(
            storage_uri=values["data_uri"],
            data_type=values["data_type"],
        )

    @staticmethod
    def load_drift_report(values):

        if bool(values.get("drift_uri")):
            return load_record_data_from_storage(
                storage_uri=values["drift_uri"],
                data_type="dict",
            )
        return None
