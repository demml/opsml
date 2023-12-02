# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from abc import ABC, abstractmethod
from typing import Any, Dict, Union, cast

import numpy as np
import pyarrow as pa

from opsml.registry.data.types import (
    AllowedDataType,
    PandasDataFrame,
    PolarsDataFrame,
    PolarsSchemaDict,
    ArrowTable,
)


ValidArrowData = Union[np.ndarray, PandasDataFrame, PolarsDataFrame, pa.Table]


# changing input type to any to handle a variety of data types which may be optionally installed (polars)
class ArrowFormatter(ABC):
    @staticmethod
    @abstractmethod
    def convert(data: Any) -> ArrowTable:
        """Converts data to pyarrow"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def validate_data(data_type: str) -> bool:
        """Validate data to formatter"""
        raise NotImplementedError


class PolarsFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: PolarsDataFrame) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data:
                Polar dataframe

        Returns
            ArrowTable pydantic class containing table and table type
        """

        return ArrowTable(table=data.to_arrow())

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.POLARS == data_type


class PandasFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: PandasDataFrame) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data:
                Pandas dataframe to convert

        Returns
            ArrowTable pydantic class containing table and table type
        """

        pa_table = pa.Table.from_pandas(data, preserve_index=False)

        return ArrowTable(table=pa_table)

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.PANDAS == data_type


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

        return ArrowTable(table=data)

    @staticmethod
    def validate_data(data_type: str):
        return AllowedDataType.NUMPY == data_type


class ArrowTableFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: pa.Table) -> ArrowTable:
        """Take pyarrow table and returns pyarrow table

        Args:
            data (pyarrow table): Pyarrow table

        Returns
            ArrowTable pydantic class containing table and table type
        """

        return ArrowTable(table=data)

    @staticmethod
    def validate_data(data_type: str):
        return AllowedDataType.PYARROW == data_type


# Run tests for data formatter
class DataFormatter:
    @staticmethod
    def convert_data_to_arrow(
        data: Union[
            pa.Table,
            PandasDataFrame,
            PolarsDataFrame,
            np.ndarray,
        ],
        data_type: str,
    ) -> ArrowTable:
        """
        Converts a pandas dataframe or numpy array into a py arrow table.
        Args:
            data:
                Pandas dataframe or numpy array.
            data_type:
                Data type of data.
        Returns:
            py arrow table
        """

        converter = next(
            (
                arrow_formatter
                for arrow_formatter in ArrowFormatter.__subclasses__()
                if arrow_formatter.validate_data(data_type=data_type)
            )
        )

        return converter.convert(data=data)

    @staticmethod
    def create_table_schema(
        data: ValidArrowData,
        data_type: str,
    ) -> Dict[str, Any]:
        """
        Generates a schema (column: type) from a py arrow table.
        Args:
            data: py arrow table.
        Returns:
            schema: Dict[str,str]
        """
        if data_type == AllowedDataType.PANDAS:
            import pandas as pd

            data = cast(pd.DataFrame, data)
            return data.dtypes.to_dict()

        if data_type == AllowedDataType.POLARS:
            import polars as pl

            data = cast(pl.DataFrame, data)
            return cast(Dict[str, Any], data.schema)

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
        data: PolarsDataFrame,
        schema: PolarsSchemaDict,
    ):
        """Instantiates schema validator for Polars dataframes

        Args:
            data:
                Polars dataframe
            schema:
                Polars schema
        """

        super().__init__(data=data, schema=schema)

    def validate_schema(self) -> PolarsDataFrame:
        """Validate polars schema. Columns are converted if schema does not match"""
        import polars as pl

        if self.data.schema != self.schema:
            self.data = self.data.with_columns([pl.col(col).cast(self.schema[col]) for col in self.data.columns])

        return self.data

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.POLARS == data_type


class PandasSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: PandasDataFrame,
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

    def validate_schema(self) -> PandasDataFrame:
        """Validate pandas schema. Columns are converted if schema does not match"""

        if self.data.dtypes.to_dict() != self.schema:
            for col in self.data.columns:
                self.data[col] = self.data[col].astype(self.schema[col])

        return cast(PandasDataFrame, self.data)

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.PANDAS == data_type


def check_data_schema(
    data: ValidArrowData,
    schema: Dict[str, str],
    data_type: str,
) -> ValidArrowData:
    """Check if data schema matches schema

    Args:
        data:
            Data to check schema
        schema:
            Schema to check
        data_type:
            Data type of data
    """
    validator = next(
        (
            validator
            for validator in SchemaValidator.__subclasses__()
            if validator.validate_data(
                data_type=data_type,
            )
        ),
        None,
    )

    if validator is None:
        return data
    return validator(data=data, schema=schema).validate_schema()
