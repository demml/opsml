# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import warnings
from typing import List, Tuple, Union

from opsml.types import DataDtypes

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from skl2onnx.common import data_types as onnx_data_types


class BaseTensorType:
    def __init__(self, dtype: str, input_shape: Union[Tuple[int, ...], List[int]]):
        self.input_shape = input_shape
        self.dtype = dtype

    def get_tensor_type(self) -> onnx_data_types.TensorType:
        raise NotImplementedError

    @staticmethod
    def validate(dtype: str) -> bool:
        raise NotImplementedError


class Float32Tensor(BaseTensorType):
    def get_tensor_type(self) -> onnx_data_types.FloatTensorType:
        return onnx_data_types.FloatTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.FLOAT32


class Float64Tensor(BaseTensorType):
    def get_tensor_type(self) -> onnx_data_types.DoubleTensorType:
        return onnx_data_types.DoubleTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.FLOAT64


class Int32Tensor(BaseTensorType):
    def get_tensor_type(self) -> onnx_data_types.Int32TensorType:
        return onnx_data_types.Int32TensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.INT32


class Int64Tensor(BaseTensorType):
    def get_tensor_type(self) -> onnx_data_types.Int64TensorType:
        return onnx_data_types.Int64TensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.INT64


class StringTensor(BaseTensorType):
    def get_tensor_type(self) -> onnx_data_types.StringTensorType:
        return onnx_data_types.StringTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.STRING


def get_skl2onnx_onnx_tensor_spec(
    dtype: str,
    input_shape: Union[Tuple[int, ...], List[int]],
) -> onnx_data_types.TensorType:
    """Takes a dtype and input shape and returns Onnx Tensor type proto to be
    used with Onnx model

    Args:
        dtype (str): Dtype of data
        input_shape (list(int)): Input shape of data

    Returns:
        Onnx TensorType
    """
    tensor_type = next(
        (
            tensor_type
            for tensor_type in BaseTensorType.__subclasses__()
            if tensor_type.validate(
                dtype=dtype,
            )
        ),
        StringTensor,
    )

    return tensor_type(
        dtype=dtype,
        input_shape=input_shape,
    ).get_tensor_type()
