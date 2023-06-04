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


class SplitModel(BaseModel):
    label: str
    column: Optional[str] = None
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


class Splitter:
    def __init__(
        self,
        split_attributes: Dict[str, Any],
        dependent_vars: Optional[List[Union[int, str]]] = None,
    ):
        self.split_attr = SplitModel(**split_attributes)
        self.dependent_vars = dependent_vars

    def split(self, data):
        raise NotImplementedError

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        raise NotImplementedError


class PolarsColumnSplitter(Splitter):
    """Column splitter for Polars dataframe"""

    def split(self, data: pl.DataFrame) -> Tuple[str, Data]:
        if self.split_attr.inequality is None:
            data = data.filter(pl.col(self.split_attr.column) == self.split_attr.column_value)

        elif self.split_attr.inequality == ">=":
            data = data.filter(pl.col(self.split_attr.column) >= self.split_attr.column_value)

        elif self.split_attr.inequality == ">":
            data = data.filter(pl.col(self.split_attr.column) > self.split_attr.column_value)

        elif self.split_attr.inequality == "<=":
            data = data.filter(pl.col(self.split_attr.column) < self.split_attr.column_value)

        else:
            data = data.filter(pl.col(self.split_attr.column) <= self.split_attr.column_value)

        if self.dependent_vars is not None:
            x_cols = data.columns
            for var in self.dependent_vars:
                x_cols.remove(var)

            return self.split_attr.label, Data(
                X=data.select(x_cols),
                y=data.select(self.dependent_vars),
            )

        return self.split_attr.label, Data(X=data)

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pl.DataFrame and split_dict.get("column") is not None


class PandasIndexSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        if self.dependent_vars is not None:
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split_attr.label, Data(
                X=x.iloc[self.split_attr.indices],
                y=y.iloc[self.split_attr.indices],
            )

        return self.split_attr.label, Data(X=data.iloc[self.split_attr.indices])

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("indices") is not None


class PandasRowSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
        if self.dependent_vars is not None:
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split_attr.label, Data(
                X=x[self.split_attr.start : self.split_attr.stop],
                y=y[self.split_attr.start : self.split_attr.stop],
            )

        return self.split_attr.label, Data(X=data[self.split_attr.start : self.split_attr.stop])

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("start") is not None


class PandasColumnSplitter(Splitter):
    def split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        if self.split_attr.inequality is None:
            data = data[data[self.split_attr.column] == self.split_attr.column_value]

        elif self.split_attr.inequality == ">":
            data = data[data[self.split_attr.column] > self.split_attr.column_value]

        elif self.split_attr.inequality == ">=":
            data = data[data[self.split_attr.column] >= self.split_attr.column_value]

        elif self.split_attr.inequality == "<":
            data = data[data[self.split_attr.column] < self.split_attr.column_value]

        else:
            data = data[data[self.split_attr.column] <= self.split_attr.column_value]

        if self.dependent_vars is not None:
            return self.split_attr.label, Data(
                x=data[data.columns[~data.columns.isin(self.dependent_vars)]],
                y=data[data.columns[data.columns.isin(self.dependent_vars)]],
            )

        data_split = Data(X=data)
        return self.split_attr.label, data_split

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pd.DataFrame and split_dict.get("column") is not None


class PyArrowIndexSplitter(Splitter):
    def split(self, data: pa.Table) -> Tuple[str, Data]:
        return self.split_attr.label, Data(X=data.take(self.split_attr.indices))

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == pa.Table and split_dict.get("indices") is not None


class NumpyIndexSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, Data]:
        return self.split_attr.label, Data(X=data[self.split_attr.indices])

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == np.ndarray and split_dict.get("indices") is not None


class NumpyRowSplitter(Splitter):
    def split(self, data: np.ndarray) -> Tuple[str, Data]:
        data_split = data[self.split_attr.start : self.split_attr.stop]
        return self.split_attr.label, Data(X=data_split)

    @staticmethod
    def validate(data_type: type, split_dict: Dict[str, Any]):
        return data_type == np.ndarray and split_dict.get("start") is not None


class DataSplitter:
    def __init__(
        self,
        split_attributes: Dict[str, Any],
        dependent_vars: Optional[List[Union[int, str]]] = None,
    ):
        self.split_attr = split_attributes
        self.dependent_vars = dependent_vars

    def split(self, data: Union[pd.DataFrame, np.ndarray]):
        splitter = next(
            (
                splitter
                for splitter in Splitter.__subclasses__()
                if splitter.validate(
                    data_type=type(data),
                    split_dict=self.split_attr,
                )
            ),
            None,
        )

        if splitter is None:
            raise ValueError("Failed to find data supporter that supports provided logic")

        data_splitter = splitter(
            split_attributes=self.split_attr,
            dependent_vars=self.dependent_vars,
        )
        return data_splitter.split(data=data)
