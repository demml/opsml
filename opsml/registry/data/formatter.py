from abc import ABC, abstractmethod
from typing import Dict, Optional, Union, Any, cast

import numpy as np
import pandas as pd
import pyarrow as pa

from .types import ArrowTable


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
    def convert(data: Any) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data (polar datagrame): Polar dataframe

        Returns
            ArrowTable pydantic class containing table and table type
        """

        import polars as pl

        data = cast(pl.DataFrame, data)

        return ArrowTable(
            table=data.to_arrow(),
            table_type="PolarsDataFrame",
        )

    @staticmethod
    def validate_data(data: Any) -> bool:
        return "polars" in str(data.__class__)


class PandasFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: Any) -> ArrowTable:
        """Convert pandas dataframe to pyarrow table

        Args:
            data (pd.DataFrame): Pandas dataframe to convert

        Returns
            ArrowTable pydantic class containing table and table type
        """

        data = cast(pd.DataFrame, data)
        pa_table = pa.Table.from_pandas(data, preserve_index=False)

        return ArrowTable(
            table=pa_table,
            table_type=data.__class__.__name__,
        )

    @staticmethod
    def validate_data(data: Any) -> bool:
        return "pandas" in str(data.__class__)


class NumpyFormatter(ArrowFormatter):
    @staticmethod
    def convert(data: Any) -> ArrowTable:
        """Convert numpy array to pyarrow table

        Args:
            data (np.ndarray): Numpy array to convert.
            Assumes data is in shape (rows, columns).

        Returns
            Numpy array
        """

        return ArrowTable(
            table=data,
            table_type=data.__class__.__name__,
        )

    @staticmethod
    def validate_data(data: Any) -> bool:
        return "numpy" in str(data.__class__)


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
            table_type=data.__class__.__name__,
        )

    @staticmethod
    def validate_data(data: Any):
        return isinstance(data, pa.Table)


# Run tests for data formatter
class DataFormatter:
    @staticmethod
    def convert_data_to_arrow(data: Any) -> ArrowTable:
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
    def create_table_schema(data: Union[pa.Table, np.ndarray]) -> Dict[str, Optional[str]]:
        """
        Generates a schema (column: type) from a py arrow table.
        Args:
            data: py arrow table.
        Returns:
            schema: Dict[str,str]
        """

        feature_map: Dict[str, Optional[str]] = {}
        if isinstance(data, pa.Table):
            schema = data.schema

            for feature, type_ in zip(schema.names, schema.types):
                feature_map[feature] = str(type_)

        elif isinstance(data, np.ndarray):
            feature_map["numpy_dtype"] = str(data.dtype)

        else:
            feature_map["data_dtype"] = None

        return feature_map
