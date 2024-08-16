# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from functools import cached_property
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.types import (
    AllowedDataType,
    CommonKwargs,
    DataDtypes,
    Feature,
    ValidModelInput,
)

logger = ArtifactLogger.get_logger()


ARRAY_TYPES = [
    AllowedDataType.NUMPY,
    AllowedDataType.TENSORFLOW_TENSOR,
    AllowedDataType.TORCH_TENSOR,
]


class ArrayHelper:
    @classmethod
    def get_tensor_stats(cls, data: Any) -> Tuple[str, Tuple[int, ...]]:
        dtype = str(data.dtype.__repr__()).lower()  # pylint: disable=unnecessary-dunder-call
        shape = tuple(data.shape)

        return dtype, shape

    @classmethod
    def get_numpy_stats(cls, data: Any) -> Tuple[str, Tuple[int, ...]]:
        dtype = str(data.dtype).lower()
        shape = data.shape
        return dtype, shape

    @classmethod
    def get_array_stats(cls, data: Any) -> Tuple[str, Tuple[int, ...]]:
        data_type = get_class_name(data)

        if data_type == AllowedDataType.NUMPY:
            return cls.get_numpy_stats(data)
        return cls.get_tensor_stats(data)


class ModelDataHelper:
    def __init__(self, input_data: Any, data_type: str):
        """Base helper class for storing input/sample data associated with a trained model.
        This class is used with OnnxModelConverter

        Args:
            input_data: Input or sample data associated with a trained model
        """
        self._data = input_data
        self._features = ["inputs"]
        self.data_type = data_type

    @property
    def data(self) -> Any:
        return self._data

    @data.setter
    def data(self, data: Any) -> None:
        self._data = data

    @property
    def all_features_float32(self) -> bool:
        return all(type_ == DataDtypes.FLOAT32 for type_ in self.dtypes)

    @property
    def has_float64(self) -> bool:
        return any(type_ == DataDtypes.FLOAT64 for type_ in self.dtypes)

    @property
    def has_category(self) -> bool:
        return any(type_ == "category" for type_ in self.dtypes)

    @property
    def features(self) -> List[str]:
        return self._features

    @features.setter
    def features(self, features: List[str]) -> None:
        self._features = features

    @property
    def feature_types(self) -> Iterator[Tuple[str, str]]:
        """Creates feature, type mapping"""
        return zip(self.features, self.dtypes)

    @property
    def dtypes(self) -> List[str]:
        raise NotImplementedError

    @property
    def shape(self) -> Any:
        raise NotImplementedError

    @property
    def num_dtypes(self) -> int:
        return len(self.dtypes)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        raise NotImplementedError

    def to_numpy(self) -> NDArray[Any]:
        raise ValueError("This method is not implemented for this Data type")

    def dataframe_record(self) -> Dict[str, Any]:
        raise ValueError("This method is not implemented for this Data type")

    def convert_dataframe_column(self, column_type: str, convert_column_type: type) -> None:
        raise ValueError("This method is not implemented for this Data type")

    @staticmethod
    def get_feature_info(type_: str, shape: List[Optional[int]]) -> Feature:
        if "int" in type_:
            return Feature(feature_type="INT", shape=shape)
        if "float" in type_:
            return Feature(feature_type="FLOAT", shape=shape)
        return Feature(feature_type="STR", shape=shape)

    @staticmethod
    def validate(data_type: str) -> bool:
        raise NotImplementedError


class ArrayData(ModelDataHelper):
    """Helper for dealing with Numpy"""

    def __init__(self, input_data: Any, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

    @property
    def dtypes(self) -> List[str]:
        return [ArrayHelper.get_array_stats(self._data)[0]]

    @property
    def num_dtypes(self) -> int:
        return len(self.dtypes)

    @property
    def shape(self) -> Tuple[int, ...]:
        return ArrayHelper.get_array_stats(self._data)[1]

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_ in zip(self.features, self.dtypes):
            feature_dict[feature] = Feature(feature_type=type_, shape=self.shape)
        return feature_dict

    @staticmethod
    def validate(data_type: str) -> bool:
        return data_type in ARRAY_TYPES


class PandasDataFrameData(ModelDataHelper):
    def __init__(self, input_data: Any, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

        self.data = cast(pd.DataFrame, self.data)

        if self.has_category:
            logger.warning("Category type detected, converting to string")
            self.convert_dataframe_column(column_type="category", convert_column_type=str)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_ in zip(self.features, self.dtypes):
            feature_dict[feature] = Feature(feature_type=type_, shape=(1,))
        return feature_dict

    @property
    def shape(self) -> Tuple[int, ...]:
        return cast(Tuple[int, ...], self.data.shape)

    @property
    def dtypes(self) -> List[str]:
        return [str(type_).lower() for type_ in self.data.dtypes.to_list()]

    @property
    def num_dtypes(self) -> int:
        return len(set(self.dtypes))

    @property
    def features(self) -> List[str]:
        return cast(List[str], self.data.columns)

    @features.setter
    def features(self, features: List[str]) -> None:
        self._features = features

    def to_numpy(self) -> NDArray[Any]:
        return cast(NDArray[Any], self.data.to_numpy())

    def convert_dataframe_column(self, column_type: str, convert_column_type: type) -> None:
        """Helper for converting pandas dataframe column to a new type"""

        for feature_name, feature_type in self.feature_types:
            if str(feature_type) == column_type:
                self.data[feature_name] = self.data[feature_name].astype(convert_column_type)

    def dataframe_record(self) -> Dict[str, Any]:
        return {col: self.data[col].values for col in self.features}

    @staticmethod
    def validate(data_type: str) -> bool:
        return data_type == AllowedDataType.PANDAS


class DataDictionary(ModelDataHelper):
    def __init__(self, input_data: Any, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

        self.data = cast(Dict[str, Any], self.data)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_, shape in zip(self.features, self.dtypes, self.shape):
            if not isinstance(shape, tuple):
                shape = (shape,)
            feature_dict[feature] = Feature(feature_type=type_, shape=shape)
        return feature_dict

    @property
    def shape(self) -> List[Tuple[int, ...]]:
        return self.get_dtypes_shapes[1]

    @property
    def get_dtypes_shapes(
        self,
    ) -> Tuple[List[str], List[Tuple[int, ...]]]:
        types: List[str] = []
        shapes: List[Tuple[int, ...]] = []
        for _, value in self.data.items():
            data_name = get_class_name(value)

            if data_name in ARRAY_TYPES:
                dtype, shape = ArrayHelper.get_array_stats(value)

            else:
                type_ = type(value)
                dtype = getattr(type_, "__name__", str(type_).lower())
                shape = getattr(value, "shape", (CommonKwargs.UNDEFINED.value,))  # type: ignore[arg-type]

            types.append(dtype)
            shapes.append(shape)

        return types, shapes

    @property
    def dtypes(self) -> List[str]:
        return self.get_dtypes_shapes[0]

    @property
    def num_dtypes(self) -> int:
        return len(set(self.dtypes))

    @property
    def features(self) -> List[str]:
        return list(self.data.keys())

    @features.setter
    def features(self, features: List[str]) -> None:
        self._features = features

    @staticmethod
    def validate(data_type: str) -> bool:
        return data_type in [AllowedDataType.DICT, AllowedDataType.ORDERED_DICT]


class IterData(ModelDataHelper):
    def __init__(self, input_data: Union[List[Any], Tuple[Any]], data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

        self.data = cast(Union[List[Any], Tuple[Any]], self.data)
        self._features = [f"input_{i}" for i in range(len(self.data))]

    @cached_property
    def get_dtypes_shapes(self) -> Tuple[List[str], List[Tuple[int, ...]]]:
        types: List[str] = []
        shapes: List[Tuple[int, ...]] = []

        for value in self.data:
            data_name = get_class_name(value)

            if data_name in ARRAY_TYPES:
                dtype, shape = ArrayHelper.get_array_stats(value)

            else:
                type_ = type(value)
                dtype = getattr(type_, "__name__", str(type_).lower())
                shape = getattr(value, "shape", (CommonKwargs.UNDEFINED.value,))  # type: ignore[arg-type]

            types.append(dtype)
            shapes.append(shape)

        return types, shapes

    @property
    def dtypes(self) -> List[str]:
        return self.get_dtypes_shapes[0]

    @property
    def shape(self) -> List[Tuple[int, ...]]:
        return self.get_dtypes_shapes[1]

    @property
    def num_dtypes(self) -> int:
        return len(set(self.dtypes))

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_, shape in zip(self.features, self.dtypes, self.shape):
            if not isinstance(shape, tuple):
                shape = (shape,)
            feature_dict[feature] = Feature(feature_type=type_, shape=shape)
        return feature_dict

    @property
    def features(self) -> List[str]:
        return self._features

    @features.setter
    def features(self, features: List[str]) -> None:
        self._features = features

    @staticmethod
    def validate(data_type: str) -> bool:
        return data_type in [AllowedDataType.TUPLE, AllowedDataType.LIST]


class StrData(ModelDataHelper):
    def __init__(self, input_data: str, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

        self.data = cast(str, self.data)
        self._features = ["input"]

    @property
    def dtypes(self) -> List[str]:
        return ["str"]

    @property
    def shape(self) -> List[Tuple[int]]:
        shape = [(0,)]
        return shape

    @property
    def num_dtypes(self) -> int:
        return len(set(self.dtypes))

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_ in zip(self.features, self.dtypes):
            feature_dict[feature] = Feature(feature_type=type_, shape=self.shape)
        return feature_dict

    @staticmethod
    def validate(data_type: str) -> bool:
        return data_type == AllowedDataType.STR


class ImageFileData(ModelDataHelper):
    """Helper for dealing with Numpy"""

    def __init__(self, input_data: Any, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

    @property
    def dtypes(self) -> List[str]:
        return [self._data.__class__.__name__]

    @property
    def num_dtypes(self) -> int:
        return len(self.dtypes)

    @property
    def shape(self) -> Tuple[int, ...]:
        if hasattr(self._data, "height"):
            height = getattr(self._data, "height") or 0
        if hasattr(self._data, "width"):
            width = getattr(self._data, "width") or 0

        return (height, width)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_ in zip(self.features, self.dtypes):
            feature_dict[feature] = Feature(feature_type=type_, shape=self.shape)
        return feature_dict

    @staticmethod
    def validate(data_type: str) -> bool:
        return "ImageFile" in data_type


class DMatrixData(ModelDataHelper):
    def __init__(self, input_data: Any, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

    @property
    def features(self) -> List[str]:
        return getattr(self._data, "feature_names", None) or ["inputs"]

    @features.setter
    def features(self, features: List[str]) -> None:
        self._features = features

    @property
    def dtypes(self) -> List[str]:
        dtypes = getattr(self._data, "feature_types", None)
        if dtypes is None:
            return [CommonKwargs.UNDEFINED.value for _ in range(len(self.features))]
        return cast(List[str], dtypes)

    @property
    def shape(self) -> Tuple[int, ...]:
        if len(self.features) == 1:
            num_cols = getattr(self._data, "num_col", None)
            if num_cols is not None:
                return (num_cols(),)
        return (1,)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        feature_dict = {}
        for feature, type_ in zip(self.features, self.dtypes):
            feature_dict[feature] = Feature(feature_type=type_, shape=self.shape)
        return feature_dict

    @staticmethod
    def validate(data_type: str) -> bool:
        return "xgboost.core.DMatrix" in data_type


class NumericData(ModelDataHelper):
    def __init__(self, input_data: str, data_type: str):
        super().__init__(input_data=input_data, data_type=data_type)

    @property
    def dtypes(self) -> List[str]:
        return [self.data_type]

    @property
    def shape(self) -> Tuple[int, ...]:
        return (0,)

    @property
    def feature_dict(self) -> Dict[str, Feature]:
        return {"inputs": Feature(feature_type=self.dtypes[0], shape=self.shape)}

    @staticmethod
    def validate(data_type: str) -> bool:
        return ("int" in data_type) or ("float" in data_type)


def get_model_data(data_type: str, input_data: Any) -> ModelDataHelper:
    """Sets the appropriate ModelData subclass depending
    on data_type passed

    Args:
        data_type (type): Data type
        input_data (Any): Input data for model
    """

    model_data = next(
        data_class
        for data_class in ModelDataHelper.__subclasses__()
        if data_class.validate(
            data_type=data_type,
        )
    )

    return model_data(input_data=input_data, data_type=data_type)


class FloatTypeConverter:
    def __init__(self, convert_all: bool):
        """Helper for converting float type or all columns to Float32

        Args:
            all (bool): Boolean indicating whether to convert all columns or not
        """
        self.convert_all = convert_all

    def _convert_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        for feature, feature_type in zip(data.columns, data.dtypes):
            if not self.convert_all:
                if DataDtypes.FLOAT64 in str(feature_type):
                    data = data.astype({feature: np.float32}, copy=False)
            else:
                data = data.astype({feature: np.float32})

        return data

    def _convert_array(self, data: NDArray[Any]) -> NDArray[Any]:
        dtype = str(data.dtype)
        if dtype != DataDtypes.STRING:
            data = data.astype(np.float32, copy=False)
        return data

    def _convert_dict(self, data: Dict[str, NDArray[Any]]) -> Dict[str, NDArray[Any]]:
        for key, value in data.items():
            dtype = str(value.dtype)
            if not self.convert_all:
                if dtype == DataDtypes.FLOAT64:
                    data[key] = value.astype(np.float32)
            else:
                if dtype != DataDtypes.STRING:
                    data[key] = value.astype(np.float32)

        return data

    def convert_to_float(self, data: ValidModelInput) -> ValidModelInput:
        if isinstance(data, pd.DataFrame):
            return self._convert_dataframe(data=data)
        if isinstance(data, np.ndarray):
            return self._convert_array(data=data)

        return self._convert_dict(data=cast(Dict[str, NDArray[Any]], data))
