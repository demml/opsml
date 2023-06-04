# pylint: disable=invalid-name
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
import numpy as np
import pandas as pd
import pyarrow as pa
from pydantic import BaseModel, Extra, validator


class DataHolder(BaseModel):
    """Class for holding data objects"""

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow


@dataclass
class Data:
    X: Union[pd.DataFrame, pa.Table, np.ndarray]
    y: Optional[Union[pd.DataFrame, pa.Table, np.ndarray]] = None


class DataSplit(BaseModel):
    label: str
    column_name: Optional[str] = None
    column_value: Optional[Any] = None
    inequality: Optional[str] = None
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

    @validator("inequality", pre=True)
    def trim_whitespace(cls, value):  # pylint: disable=no-self-argument
        """Trims whitespace from inequality signs"""

        if value is not None:
            value = value.strip()

        return value


class DataSplitterBase:
    def __init__(
        self,
        split: DataSplit,
        dependent_vars: Optional[List[Union[int, str]]] = None,
    ):
        self.split = split
        self.dependent_vars = dependent_vars

    def create_split(self, data):
        raise NotImplementedError

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        raise NotImplementedError


class PolarsColumnSplitter(DataSplitterBase):
    """Column splitter for Polars dataframe"""

    def create_split(self, data: pl.DataFrame) -> Tuple[str, Data]:
        if self.split.inequality is None:
            data = data.filter(pl.col(self.split.column_name) == self.split.column_value)

        elif self.split.inequality == ">":
            data = data.filter(pl.col(self.split.column_name) > self.split.column_value)

        elif self.split.inequality == ">=":
            data = data.filter(pl.col(self.split.column_name) >= self.split.column_value)

        elif self.split.inequality == "<":
            data = data.filter(pl.col(self.split.column_name) < self.split.column_value)

        else:
            data = data.filter(pl.col(self.split.column_name) <= self.split.column_value)

        if self.dependent_vars is not None:
            x_cols = data.columns
            for var in self.dependent_vars:
                x_cols.remove(var)

            return self.split.label, Data(
                X=data.select(x_cols),
                y=data.select(self.dependent_vars),
            )

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == pl.DataFrame and split.column_name is not None


class PandasIndexSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        if self.dependent_vars is not None:
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split.label, Data(
                X=x.iloc[self.split.indices],
                y=y.iloc[self.split.indices],
            )

        return self.split.label, Data(X=data.iloc[self.split.indices])

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == pd.DataFrame and split.indices is not None


class PandasRowSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        if self.dependent_vars is not None:
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split.label, Data(
                X=x[self.split.start : self.split.stop],
                y=y[self.split.start : self.split.stop],
            )

        return self.split.label, Data(X=data[self.split.start : self.split.stop])

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == pd.DataFrame and split.start is not None


class PandasColumnSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        if self.split.inequality is None:
            data = data[data[self.split.column_name] == self.split.column_value]

        elif self.split.inequality == ">":
            data = data[data[self.split.column_name] > self.split.column_value]

        elif self.split.inequality == ">=":
            data = data[data[self.split.column_name] >= self.split.column_value]

        elif self.split.inequality == "<":
            data = data[data[self.split.column_name] < self.split.column_value]

        else:
            data = data[data[self.split.column_name] <= self.split.column_value]

        if self.dependent_vars is not None:
            return self.split.label, Data(
                X=data[data.columns[~data.columns.isin(self.dependent_vars)]],
                y=data[data.columns[data.columns.isin(self.dependent_vars)]],
            )

        data_split = Data(X=data)
        return self.split.label, data_split

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == pd.DataFrame and split.column_name is not None


class PyArrowIndexSplitter(DataSplitterBase):
    def create_split(self, data: pa.Table) -> Tuple[str, Data]:
        return self.split.label, Data(X=data.take(self.split.indices))

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == pa.Table and split.indices is not None


class NumpyIndexSplitter(DataSplitterBase):
    def create_split(self, data: np.ndarray) -> Tuple[str, Data]:
        return self.split.label, Data(X=data[self.split.indices])

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == np.ndarray and split.indices is not None


class NumpyRowSplitter(DataSplitterBase):
    def create_split(self, data: np.ndarray) -> Tuple[str, Data]:
        data_split = data[self.split.start : self.split.stop]
        return self.split.label, Data(X=data_split)

    @staticmethod
    def validate(data_type: type, split: DataSplit):
        return data_type == np.ndarray and split.start is not None


class DataSplitter:
    @staticmethod
    def split(
        split: DataSplit,
        data: Union[pd.DataFrame, np.ndarray, pl.DataFrame],
        dependent_vars: Optional[List[Union[int, str]]] = None,
    ):
        data_splitter = next(
            (
                data_splitter
                for data_splitter in DataSplitterBase.__subclasses__()
                if data_splitter.validate(
                    data_type=type(data),
                    split=split,
                )
            ),
            None,
        )

        if data_splitter is None:
            raise ValueError("Failed to find data supporter that supports provided logic")

        data_splitter = data_splitter(split=split, dependent_vars=dependent_vars)
        return data_splitter.create_split(data=data)
