from enum import Enum
from typing import Dict, List, Optional, Union

import numpy as np
import pyarrow as pa
from pydantic import BaseModel, Extra, root_validator


class SplitDataHolder(BaseModel):

    """Pydantic model to hold split data"""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow


class DataSplit(BaseModel):
    label: Optional[str] = None
    col: Optional[str] = None
    val: Optional[Union[int, str]] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    row_slicing: bool = False

    @root_validator(pre=True)
    def set_attributes(cls, values):  # pylint: disable=no-self-argument
        """Pre checks"""

        no_column_slicing = any(i is None for i in [values.get("col"), values.get("val")])
        no_row_slicing = any(i is None for i in [values.get("start"), values.get("stop")])

        # User must supply one or the other

        if no_column_slicing and no_row_slicing:

            raise ValueError(
                """Split dictionary must either contain 'col' and 'val' keys or 'start' and 'stop'
            """
            )

        if no_column_slicing:
            values["row_slicing"] = True

        return values


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
    feature_map: Optional[Dict[str, str]]

    class Config:
        arbitrary_types_allowed = True


class RegistryRecord(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None
    data_splits: Optional[List[DataSplit]] = None
    version: int
    data_type: str
    data_name: str
    team: str
    feature_map: Dict[str, str]
    user_email: str
    uid: Optional[str] = None
    version: Optional[int] = None
