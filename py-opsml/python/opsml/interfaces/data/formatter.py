# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast
from opsml import Feature

import pandas as pd
import polars as pl
import pyarrow as pa
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.types import AllowedDataType

logger = ArtifactLogger.get_logger()

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
    def generate_feature_map(data: Any) -> Dict[str, Feature]:
        """Generate feature map"""
        raise NotImplementedError

    @staticmethod
    def validate_data(data_type: str) -> bool:
        """Validate data to formatter"""
        raise NotImplementedError


class PolarsType:
    """Base class for Polars types"""

    @staticmethod
    def as_feature(data_type: Any) -> Feature:
        """Convert Polars type to Feature"""
        raise NotImplementedError

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:
        """Cast Polars type"""
        raise NotImplementedError

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        """Validate data type"""
        raise NotImplementedError


class DecimalType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Decimal) -> Feature:
        return Feature(
            feature_type="decimal",
            shape=(1,),
            extra_args={
                "precision": data_type.precision,
                "scale": data_type.scale,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        precision = cast(Optional[int], feature.extra_args.get("precision"))
        scale = cast(int, feature.extra_args.get("scale"))

        return pl.col(data).cast(pl.Decimal(precision, scale))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "decimal"

        return isinstance(data_type, pl.Decimal)


class DateTimeType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.DataType) -> Feature:
        return Feature(
            feature_type="datetime",
            shape=(1,),
            extra_args={
                "time_unit": data_type.time_unit,
                "time_zone": data_type.time_zone,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        time_unit = cast(Literal["ns", "us", "ms"], feature.extra_args.get("time_unit"))
        time_zone = cast(Optional[str], feature.extra_args.get("time_zone"))

        return pl.col(data).cast(pl.Datetime(time_unit, time_zone))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "datetime"

        return isinstance(data_type, pl.Datetime)


class DurationType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Duration) -> Feature:
        assert isinstance(data_type, pl.Duration)
        return Feature(
            feature_type="duration",
            shape=(1,),
            extra_args={
                "time_unit": data_type.time_unit,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        time_unit = cast(Literal["ns", "us", "ms"], feature.extra_args.get("time_unit"))
        return pl.col(data).cast(pl.Duration(time_unit))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "duration"

        return isinstance(data_type, pl.Duration)


class CategoricalType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Categorical) -> Feature:
        return Feature(
            feature_type="categorical",
            shape=(1,),
            extra_args={
                "ordering": data_type.ordering,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        ordering = cast(
            Optional[Literal["physical", "lexical"]], feature.extra_args.get("ordering")
        )
        return pl.col(data).cast(pl.Categorical(ordering))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "categorical"

        return isinstance(data_type, pl.Categorical)


class EnumType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Enum) -> Feature:
        if isinstance(data_type.categories, pl.Series):
            categories = data_type.categories.to_list()
        else:
            categories = cast(List[str], data_type.categories)

        return Feature(
            feature_type="enum",
            shape=(1,),
            extra_args={
                "categories": categories,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        categories = cast(List[str], feature.extra_args["categories"])
        return pl.col(data).cast(pl.Enum(categories))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "enum"

        return isinstance(data_type, pl.Enum)


class ListType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.List) -> Feature:
        return Feature(
            feature_type="list",
            shape=(1,),
            extra_args={"inner": str(data_type.inner)},
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        _inner_type = cast(str, feature.extra_args.get("inner"))
        inner_type = getattr(pl, _inner_type)
        return pl.col(data).cast(pl.List(inner_type))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "list"

        return isinstance(data_type, pl.List)


class ArrayType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Array) -> Feature:
        return Feature(
            feature_type="array",
            shape=data_type.shape,
            extra_args={
                "inner": str(data_type.inner),
                "size": data_type.size,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        _inner_type = cast(str, feature.extra_args.get("inner"))
        inner_type = getattr(pl, _inner_type)
        size = cast(
            Optional[Union[int, Tuple[int, ...]]], feature.extra_args.get("size")
        )

        return pl.col(data).cast(
            pl.Array(
                inner=inner_type,
                shape=size,
            ),
        )

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "array"

        return isinstance(data_type, pl.Array)


class StructType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.Struct) -> Feature:
        fields = [
            {
                "name": field.name,
                "data_type": str(field.dtype),
            }
            for field in data_type.fields
        ]
        return Feature(
            feature_type="struct",
            shape=data_type.shape,
            extra_args={
                "fields": fields,
            },
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        _fields = cast(List[Dict[str, str]], feature.extra_args.get("fields"))
        fields = [
            pl.Field(name=field["name"], dtype=getattr(pl, field["data_type"]))
            for field in _fields
        ]
        return pl.col(data).cast(pl.Struct(fields=fields))

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        if isinstance(data_type, str):
            return data_type == "struct"

        return isinstance(data_type, pl.Struct)


class DefaultPolarsType(PolarsType):
    @staticmethod
    def as_feature(data_type: pl.DataType) -> Feature:
        return Feature(
            feature_type=str(data_type),
            shape=(1,),
        )

    @staticmethod
    def cast(data: Any, feature: Feature) -> Any:  # TODO: Fix Any
        data_type = getattr(pl, str(feature.feature_type))
        return pl.col(data).cast(data_type)

    @staticmethod
    def is_type(data_type: Union[pl.DataType, str]) -> bool:
        return False


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
        assert isinstance(self.data, pl.DataFrame), "Data is not a Polars DataFrame"

        # polars schema should be inferred from the arrow table by default.
        # This is secondary check, so we implement a soft failure.
        try:
            _check_cols = []

            for col in self.data.columns:
                schema_type = next(
                    (
                        validator
                        for validator in PolarsType.__subclasses__()
                        if validator.is_type(
                            data_type=self.schema[col].feature_type,
                        )
                    ),
                    DefaultPolarsType,
                )

                _check_cols.append(schema_type.cast(data=col, feature=self.schema[col]))

            return self.data.with_columns(_check_cols)
        except Exception as error:
            logger.warning(
                f"Failed to validate schema: {error}. Returning original data"
            )
            raise error
            # return self.data

    @staticmethod
    def generate_feature_map(data: pl.DataFrame) -> Dict[str, Feature]:
        feature_map: Dict[str, Feature] = {}

        for key, value in data.schema.items():
            schema_type = next(
                (
                    validator
                    for validator in PolarsType.__subclasses__()
                    if validator.is_type(
                        data_type=value,
                    )
                ),
                DefaultPolarsType,
            )
            feature_map[key] = schema_type.as_feature(data_type=value)

        return feature_map

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
    def generate_feature_map(data: pd.DataFrame) -> Dict[str, Feature]:
        return {
            key: Feature(
                feature_type=str(value),
                shape=(1,),
            )
            for key, value in data.dtypes.to_dict().items()
        }

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.PANDAS == data_type


class NumpySchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: NDArray[Any],
        schema: Dict[str, Feature],
    ):
        """Instantiates schema validator for Numpy arrays

        Args:
            data:
                Numpy array
            schema:
                Numpy schema
        """
        super().__init__(data=data, schema=schema)

    def validate_schema(self) -> NDArray[Any]:
        """Validate numpy schema. Columns are converted if schema does not match"""
        raise NotImplementedError

    @staticmethod
    def generate_feature_map(data: NDArray[Any]) -> Dict[str, Feature]:
        return {
            "features": Feature(
                feature_type=str(data.dtype),
                shape=data.shape,
            )
        }

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.NUMPY == data_type


class ArrowSchemaValidator(SchemaValidator):
    def __init__(
        self,
        data: pa.Table,
        schema: Dict[str, Feature],
    ):
        """Instantiates schema validator for Arrow tables

        Args:
            data:
                Arrow table
            schema:
                Arrow schema
        """
        super().__init__(data=data, schema=schema)

    def validate_schema(self) -> pa.Table:
        """Validate arrow schema. Columns are converted if schema does not match"""
        raise NotImplementedError

    @staticmethod
    def generate_feature_map(data: pa.Table) -> Dict[str, Feature]:
        schema = data.schema

        return {
            feature: Feature(
                feature_type=str(type_),
                shape=(1,),
            )
            for feature, type_ in zip(schema.names, schema.types)
        }

    @staticmethod
    def validate_data(data_type: str) -> bool:
        return AllowedDataType.PYARROW == data_type


def generate_feature_schema(data: ValidArrowData, data_type: str) -> Dict[str, Feature]:
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
        return {}

    return validator.generate_feature_map(data)


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
