# pylint: disable=invalid-name
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import polars as pl
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, field_validator

from opsml.types import AllowedDataType


@dataclass
class Data:
    X: Any
    y: Optional[Any] = None


class DataSplit(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    label: str
    column_name: Optional[str] = None
    column_value: Optional[Union[str, float, int, pd.Timestamp]] = None
    inequality: Optional[str] = None
    start: Optional[int] = None
    stop: Optional[int] = None
    indices: Optional[List[int]] = None

    @field_validator("indices", mode="before")
    @classmethod
    def convert_to_list(cls, value: Optional[List[int]]) -> Optional[List[int]]:
        """Pre to convert indices to list if not None"""

        if value is not None and not isinstance(value, list):
            value = list(value)

        return value

    @field_validator("inequality", mode="before")
    @classmethod
    def trim_whitespace(cls, value: str) -> str:
        """Trims whitespace from inequality signs"""

        if value is not None:
            value = value.strip()

        return value


class DataSplitterBase:
    def __init__(
        self,
        split: DataSplit,
        dependent_vars: List[Union[int, str]],
    ):
        self.split = split
        self.dependent_vars = dependent_vars

    @property
    def column_name(self) -> str:
        if self.split.column_name is not None:
            return self.split.column_name

        raise ValueError("Column name was not provided")

    @property
    def column_value(self) -> Any:
        if self.split.column_value is not None:
            return self.split.column_value

        raise ValueError("Column value was not provided")

    @property
    def indices(self) -> List[int]:
        if self.split.indices is not None:
            return self.split.indices
        raise ValueError("List of indices was not provided")

    @property
    def start(self) -> int:
        if self.split.start is not None:
            return self.split.start
        raise ValueError("Start index was not provided")

    @property
    def stop(self) -> int:
        if self.split.stop is not None:
            return self.split.stop
        raise ValueError("Stop index was not provided")

    def get_x_cols(self, columns: List[str], dependent_vars: List[Union[str, int]]) -> List[str]:
        for var in dependent_vars:
            if isinstance(var, str):
                columns.remove(var)

        return columns

    def create_split(self, data: Any) -> Tuple[str, Data]:
        raise NotImplementedError

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        raise NotImplementedError


class PolarsColumnSplitter(DataSplitterBase):
    """Column splitter for Polars dataframe"""

    def create_split(self, data: pl.DataFrame) -> Tuple[str, Data]:
        if self.split.inequality is None:
            data = data.filter(pl.col(self.column_name) == self.column_value)

        elif self.split.inequality == ">":
            data = data.filter(pl.col(self.column_name) > self.column_value)

        elif self.split.inequality == ">=":
            data = data.filter(pl.col(self.column_name) >= self.column_value)

        elif self.split.inequality == "<":
            data = data.filter(pl.col(self.column_name) < self.column_value)

        else:
            data = data.filter(pl.col(self.column_name) <= self.column_value)

        if bool(self.dependent_vars):
            x_cols = self.get_x_cols(columns=data.columns, dependent_vars=self.dependent_vars)

            return self.split.label, Data(
                X=data.select(x_cols),
                y=data.select(self.dependent_vars),
            )

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.POLARS and split.column_name is not None


class PolarsIndexSplitter(DataSplitterBase):
    """Split Polars DataFrame by rows index"""

    def create_split(self, data: pl.DataFrame) -> Tuple[str, Data]:
        # slice
        data = data[self.indices]

        if bool(self.dependent_vars):
            x_cols = self.get_x_cols(columns=data.columns, dependent_vars=self.dependent_vars)

            return self.split.label, Data(
                X=data.select(x_cols),
                y=data.select(self.dependent_vars),
            )

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.POLARS and split.indices is not None


class PolarsRowsSplitter(DataSplitterBase):
    """Split Polars DataFrame by rows slice"""

    def create_split(self, data: pl.DataFrame) -> Tuple[str, Data]:
        # slice
        data = data[self.start : self.stop]

        if bool(self.dependent_vars):
            x_cols = self.get_x_cols(columns=data.columns, dependent_vars=self.dependent_vars)

            return self.split.label, Data(
                X=data.select(x_cols),
                y=data.select(self.dependent_vars),
            )

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.POLARS and split.start is not None


class PandasIndexSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        data = data.iloc[self.indices]

        if bool(self.dependent_vars):
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split.label, Data(X=x, y=y)

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.PANDAS and split.indices is not None


class PandasRowSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        # slice
        data = data[self.start : self.stop]

        if bool(self.dependent_vars):
            x = data[data.columns[~data.columns.isin(self.dependent_vars)]]
            y = data[data.columns[data.columns.isin(self.dependent_vars)]]

            return self.split.label, Data(X=x, y=y)

        return self.split.label, Data(X=data)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.PANDAS and split.start is not None


class PandasColumnSplitter(DataSplitterBase):
    def create_split(self, data: pd.DataFrame) -> Tuple[str, Data]:
        if self.split.inequality is None:
            data = data[data[self.column_name] == self.column_value]

        elif self.split.inequality == ">":
            data = data[data[self.column_name] > self.column_value]

        elif self.split.inequality == ">=":
            data = data[data[self.column_name] >= self.column_value]

        elif self.split.inequality == "<":
            data = data[data[self.column_name] < self.column_value]

        else:
            data = data[data[self.column_name] <= self.column_value]

        if bool(self.dependent_vars):
            return self.split.label, Data(
                X=data[data.columns[~data.columns.isin(self.dependent_vars)]],
                y=data[data.columns[data.columns.isin(self.dependent_vars)]],
            )

        data_split = Data(X=data)
        return self.split.label, data_split

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.PANDAS and split.column_name is not None


class PyArrowIndexSplitter(DataSplitterBase):
    def create_split(self, data: pa.Table) -> Tuple[str, Data]:
        return self.split.label, Data(X=data.take(self.indices))

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.PYARROW and split.indices is not None


class NumpyIndexSplitter(DataSplitterBase):
    def create_split(self, data: NDArray[Any]) -> Tuple[str, Data]:
        return self.split.label, Data(X=data[self.indices])

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.NUMPY and split.indices is not None


class NumpyRowSplitter(DataSplitterBase):
    def create_split(self, data: NDArray[Any]) -> Tuple[str, Data]:
        data_split = data[self.start : self.stop]
        return self.split.label, Data(X=data_split)

    @staticmethod
    def validate(data_type: str, split: DataSplit) -> bool:
        return data_type == AllowedDataType.NUMPY and split.start is not None


class DataSplitter:
    @staticmethod
    def split(
        split: DataSplit,
        data: Union[pd.DataFrame, NDArray[Any], pl.DataFrame],
        data_type: str,
        dependent_vars: List[Union[int, str]],
    ) -> Tuple[str, Data]:
        data_splitter = next(
            (
                data_splitter
                for data_splitter in DataSplitterBase.__subclasses__()
                if data_splitter.validate(
                    data_type=data_type,
                    split=split,
                )
            ),
            None,
        )

        if data_splitter is not None:
            return data_splitter(
                split=split,
                dependent_vars=dependent_vars,
            ).create_split(data=data)

        raise ValueError("Failed to find data supporter that supports provided logic")
