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
            data (polar dataframe): Polar dataframe

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
            data (pd.DataFrame): Pandas dataframe to convert

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

        elif isinstance(data, pl.DataFrame):
            return data.schema

        elif isinstance(data, pa.Table):
            schema = data.schema

            return {feature: str(type_) for feature, type_ in zip(schema.names, schema.types)}

        elif isinstance(data, np.ndarray):
            return {"numpy_dtype": str(data.dtype)}

        else:
            return {"data_type": None}
