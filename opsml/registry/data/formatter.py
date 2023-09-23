# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa

from .types import AllowedTableTypes, ArrowTable


# changing input type to any to handle a variety of data types which may be optionally installed (polars)
class ArrowFormatter(ABC):
    @staticmethod
    @abstractmethod
    def convert(data: Any) -> ArrowTable:
        """Converts data to pyarrow"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def validate_data(data: Any) -> bool:
        """Validate data to formatter"""
        raise NotImplementedError


class PolarsFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: pl.DataFrame) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data:
                Polar dataframe

        Returns
            ArrowTable pydantic class containing table and table type
        """

        return ArrowTable(
            table=data.to_arrow(),
            table_type=AllowedTableTypes.POLARS_DATAFRAME,
        )

    @staticmethod
    def validate_data(data: pl.DataFrame) -> bool:
        return isinstance(data, pl.DataFrame)


class PandasFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: pd.DataFrame) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data:
                Pandas dataframe to convert

        Returns
            ArrowTable pydantic class containing table and table type
        """

        pa_table = pa.Table.from_pandas(data, preserve_index=False)

        return ArrowTable(
            table=pa_table,
            table_type=AllowedTableTypes.PANDAS_DATAFRAME,
        )

    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        return isinstance(data, pd.DataFrame)


class NumpyFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: np.ndarray) -> ArrowTable:
        """Convert numpy array to pyarrow table

        Args:
            data (np.ndarray): Numpy array to convert.
            Assumes data is in shape (rows, columns).

        Returns
            Numpy array
        """

        return ArrowTable(
            table=data,
            table_type=AllowedTableTypes.NDARRAY,
        )

    @staticmethod
    def validate_data(data: np.ndarray) -> bool:
        return isinstance(data, np.ndarray)


class ArrowTableFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: pa.Table) -> ArrowTable:
        """Take pyarrow table and returns pyarrow table

        Args:
            data (pyarrow table): Pyarrow table

        Returns
            ArrowTable pydantic class containing table and table type
        """

        return ArrowTable(
            table=data,
            table_type=AllowedTableTypes.ARROW_TABLE,
        )

    @staticmethod
    def validate_data(data: pa.Table):
        return isinstance(data, pa.Table)


# Run tests for data formatter
class DataFormatter:
    @staticmethod
    def convert_data_to_arrow(
        data: Union[
            pa.Table,
            pl.DataFrame,
            pd.DataFrame,
            np.ndarray,
        ]
    ) -> ArrowTable:
        """
        Converts a pandas dataframe or numpy array into a py arrow table.
        Args:
            data: Pandas dataframe or numpy array.
        Returns:
            py arrow table
        """

        converter = next(
            (
                arrow_formatter
                for arrow_formatter in ArrowFormatter.__subclasses__()
                if arrow_formatter.validate_data(data=data)
            )
        )

        return converter.convert(data=data)

    @staticmethod
    def create_table_schema(
        data: Union[
            pa.Table,
            np.ndarray,
            pd.DataFrame,
            pl.DataFrame,
        ]
    ) -> Union[Dict[str, Any], pl.type_aliases.SchemaDict]:
        """
        Generates a schema (column: type) from a py arrow table.
        Args:
            data: py arrow table.
        Returns:
            schema: Dict[str,str]
        """
        if isinstance(data, pd.DataFrame):
            return data.dtypes.to_dict()

        if isinstance(data, pl.DataFrame):
            return data.schema

        if isinstance(data, pa.Table):
            schema = data.schema

            return {feature: str(type_) for feature, type_ in zip(schema.names, schema.types)}

        if isinstance(data, np.ndarray):
            return {"numpy_dtype": str(data.dtype)}

        return {"data_type": None}


class SchemaValidator:
    def __init__(
        self,
        data: Any,
        schema: Any,
    ):
        self.data = data
        self.schema = schema

    def validate_schema(self) -> Any:
        """Converts data to pyarrow"""
        raise NotImplementedError

    @staticmethod
    def validate_data(data: Any) -> bool:
        """Validate data to formatter"""
        raise NotImplementedError


class PolarsSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: pl.DataFrame,
        schema: pl.type_aliases.SchemaDict,
    ):
        """Instantiates schema validator for Polars dataframes

        Args:
            data:
                Polars dataframe
            schema:
                Polars schema
        """

        super().__init__(data=data, schema=schema)

    def validate_schema(self) -> pl.DataFrame:
        """Validate polars schema. Columns are converted if schema does not match"""

        if self.data.schema != self.schema:
            self.data = self.data.with_columns([pl.col(col).cast(self.schema[col]) for col in self.data.columns])

        return self.data

    @staticmethod
    def validate_data(data: pl.DataFrame) -> bool:
        return isinstance(data, pl.DataFrame)


class PandasSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: pd.DataFrame,
        schema: Dict[str, str],
    ):
        """Instantiates schema validator for Polars dataframes

        Args:
            data:
                Pandas dataframe
            schema:
                Pandas schema
        """
        super().__init__(data=data, schema=schema)

    def validate_schema(self) -> pd.DataFrame:
        """Validate pandas schema. Columns are converted if schema does not match"""

        if self.data.dtypes.to_dict() != self.schema:
            for col in self.data.columns:
                self.data[col] = self.data[col].astype(self.schema[col])
        return self.data

    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        return isinstance(data, pd.DataFrame)


def check_data_schema(
    data: Union[pa.Table, pl.DataFrame, pd.DataFrame, np.ndarray],
    schema: Dict[str, str],
) -> Union[pa.Table, pl.DataFrame, pd.DataFrame, np.ndarray]:
    """Check if data schema matches schema

    Args:
        data:
            Data to check schema
        schema:
            Schema to check
    """
    validator = next(
        (validator for validator in SchemaValidator.__subclasses__() if validator.validate_data(data=data)), None
    )

    if validator is None:
        return data
    return validator(data=data, schema=schema).validate_schema()
