# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Union, cast

import pandas as pd
import polars as pl
import pyarrow as pa
from numpy.typing import NDArray

from opsml.types import AllowedDataType, Feature

ValidArrowData = Union[NDArray[Any], pd.DataFrame, pl.DataFrame, pa.Table]


class SchemaValidator:
    def __init__(
        self,
        data: Any,
        schema: Dict[str, Feature],
    ):
        self.data = data
        self.schema = schema

    def validate_schema(self) -> Any:
        """Converts data to pyarrow"""
        raise NotImplementedError

    @staticmethod
    def validate_data(data_type: str) -> bool:
        """Validate data to formatter"""
        raise NotImplementedError


class PolarsSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: pl.DataFrame,
        schema: Dict[str, Feature],
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

        self.data = self.data.with_columns(
            [pl.col(col).cast(getattr(pl, self.schema[col].feature_type)) for col in self.data.columns]
        )

        return cast(pl.DataFrame, self.data)

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.POLARS == data_type


class PandasSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: pd.DataFrame,
        schema: Dict[str, Feature],
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

        for col in self.data.columns:
            self.data[col] = self.data[col].astype(self.schema[col].feature_type)

        return cast(pd.DataFrame, self.data)

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.PANDAS == data_type


def check_data_schema(
    data: ValidArrowData,
    schema: Dict[str, Feature],
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
