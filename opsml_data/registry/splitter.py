from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel, Extra


class DataHolder(BaseModel):
    """Class for holding data objects"""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow


class SplitModel(BaseModel):
    label: str
    column: Optional[str] = None
    column_value: Optional[Union[int, str]] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    indices: Optional[Union[np.ndarray, List[int]]] = None

    class Config:
        arbitrary_types_allowed = True


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
        if data_type == pd.DataFrame and split_dict.get("indices") is not None:
            return True
        return False


class PandasRowSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        return self.split_attributes.label, data[self.split_attributes.start : self.split_attributes.stop]

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        print(data_type == pd.DataFrame)
        if data_type == pd.DataFrame and split_dict.get("start") is not None:
            return True
        return False


class PandasColumnSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        data_split = data.loc[data[self.split_attributes.column] == self.split_attributes.column_value]
        return self.split_attributes.label, data_split

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        if data_type == pd.DataFrame and split_dict.get("column") is not None:
            return True
        return False


class NumpyIndexSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, np.ndarray]:
        return self.split_attributes.label, data[self.split_attributes.indices]

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        if data_type == np.ndarray and split_dict.get("indices") is not None:
            return True
        return False


class NumpyRowSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, np.ndarray]:
        data_split = data[self.split_attributes.start : self.split_attributes.stop]
        return self.split_attributes.label, data_split

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        if data_type == np.ndarray and split_dict.get("start") is not None:
            return True
        return False


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
