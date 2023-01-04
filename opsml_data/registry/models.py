from enum import Enum
from typing import Dict, List, Optional, Union, cast

import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic import BaseModel, Extra, root_validator


class SplitDataHolder(BaseModel):

    """Pydantic model to hold split data"""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow

    def set_split(
        self,
        is_row_slicing: bool,
        label: str,
        data: Union[pd.DataFrame, np.ndarray],
        start_idx: Optional[int] = None,
        stop_idx: Optional[int] = None,
        column: Optional[str] = None,
        column_value: Optional[Union[int, str]] = None,
    ):
        if is_row_slicing:
            setattr(self, label, data[start_idx:stop_idx])
        else:
            data = cast(pd.DataFrame, data)
            setattr(self, label, data.loc[data[column] == column_value])


class DataSplit(BaseModel):
    label: Optional[str] = None
    column: Optional[str] = None
    column_value: Optional[Union[int, str]] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    row_slicing: bool = False

    @root_validator(pre=True)
    def set_attributes(cls, values):  # pylint: disable=no-self-argument
        """Pre checks"""

        no_column_slicing = any(i is None for i in [values.get("column"), values.get("column_value")])
        no_row_slicing = any(i is None for i in [values.get("start"), values.get("stop")])

        # User must supply one or the other

        if no_column_slicing and no_row_slicing:

            raise ValueError(
                """Split dictionary must either contain 'column' and 'column_value' keys or 'start' and 'stop'
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
    feature_map: Optional[Dict[str, Union[str, None]]] = None

    class Config:
        arbitrary_types_allowed = True


class RegistryRecord(BaseModel):
    data_uri: str
    drift_uri: Optional[str] = None
    data_splits: Optional[Dict[str, List[DataSplit]]] = None
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
