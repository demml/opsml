from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic import BaseModel, Extra, validator


class DataHolder(BaseModel):
    """Class for holding data objects"""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow


class SplitModel(BaseModel):
    label: str
    column: Optional[str] = None
    column_value: Optional[Any] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    indices: Optional[List[int]] = None

    class Config:
        arbitrary_types_allowed = True

    @validator("indices", pre=True)
    def convert_to_list(cls, value):  # pylint: disable=no-self-argument
        """Pre to convert indices to list if not None"""

        if value is not None and not isinstance(value, list):
            value = list(value)

        return value


class Splitter:
    def __init__(self, split_attributes: Dict[str, Any]):
        self.split_attributes = SplitModel(**split_attributes)

    def split(self, data):
        """Splits data"""

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        """Validates data type"""


class PandasIndexSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        return self.split_attributes.label, data.iloc[self.split_attributes.indices]

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("indices") is not None


class PandasRowSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        return self.split_attributes.label, data[self.split_attributes.start : self.split_attributes.stop]

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("start") is not None


class PandasColumnSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        data_split = data.loc[data[self.split_attributes.column] == self.split_attributes.column_value]
        return self.split_attributes.label, data_split

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("column") is not None


class PyArrowIndexSplitter(Splitter):
    def split(self, data: pa.Table) -> Tuple[str, pa.Table]:
        return self.split_attributes.label, data.take(self.split_attributes.indices)

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pa.Table and split_dict.get("indices") is not None


class NumpyIndexSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, np.ndarray]:
        return self.split_attributes.label, data[self.split_attributes.indices]

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == np.ndarray and split_dict.get("indices") is not None


class NumpyRowSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, np.ndarray]:
        data_split = data[self.split_attributes.start : self.split_attributes.stop]
        return self.split_attributes.label, data_split

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == np.ndarray and split_dict.get("start") is not None


class DataSplitter:
    def __init__(
        self,
        split_attributes: Dict[str, Any],
    ):
        self.split_attributes = split_attributes

    def split(self, data: Union[pd.DataFrame, np.ndarray]):

        splitter = next(
            (
                splitter
                for splitter in Splitter.__subclasses__()
                if splitter.validate(
                    data_type=type(data),
                    split_dict=self.split_attributes,
                )
            )
        )

        data_splitter = splitter(split_attributes=self.split_attributes)
        return data_splitter.split(data=data)
