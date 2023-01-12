# pylint: disable=import-outside-toplevel
# break this out into separate files at some point (data_converter.py, model_converter.py)
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Tuple, Union, cast, Optional
import numpy as np
import pandas as pd
from pyshipt_logging import ShiptLogging
from skl2onnx.common.data_types import (
    FloatTensorType,
    Int32TensorType,
    Int64TensorType,
    StringTensorType,
)

from opsml_artifacts.registry.model.base_types import (
    Feature,
    ModelDefinition,
    OnnxModelType,
    AVAILABLE_MODEL_TYPES,
)

# Get logger
logger = ShiptLogging.get_logger(__name__)

ModelConvertOutput = Tuple[ModelDefinition, Dict[str, Feature], Optional[Dict[str, str]]]


class DataConverter:
    def __init__(self, data: Union[pd.DataFrame, np.ndarray]):
        self.data = data

    def get_data_schema(self) -> Optional[Dict[str, str]]:
        """Gets schema from data.
        Reproduces onnx_data_types in some instances
        """
        raise NotImplementedError

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""
        raise NotImplementedError

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Converts data to onnx schema"""
        raise NotImplementedError

    def _get_onnx_dataframe_schema(self) -> List[Any]:
        self.data = cast(pd.DataFrame, self.data)

        inputs = []
        for key, val in zip(self.data.columns, self.data.dtypes):
            if "int64" in str(val):
                tensor = Int64TensorType([None, 1])
            elif "int32" in str(val):
                tensor = Int32TensorType([None, 1])
            elif "float" in str(val):
                tensor = FloatTensorType([None, 1])
            else:
                tensor = StringTensorType([None, 1])
            inputs.append((key, tensor))
        return inputs

    def _get_py_dataframe_schema(self) -> Dict[str, str]:
        self.data = cast(pd.DataFrame, self.data)

        feature_dict: Dict[str, str] = {}
        for feature, feature_type in zip(self.data.columns, self.data.dtypes):
            if "int" in str(feature_type):
                feature_dict[feature] = "int"
            elif "float" in str(feature_type):
                feature_dict[feature] = "float"
            else:
                feature_dict[feature] = "str"
        return feature_dict

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, str]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        return [("inputs", FloatTensorType([None, self.data.shape[1]]))]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {"inputs": self.data.astype(np.float32)[:1]}

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == np.ndarray and model_type in AVAILABLE_MODEL_TYPES:
            return True
        return False


class PandasOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, str]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        self.data = cast(pd.DataFrame, self.data)
        return [("inputs", FloatTensorType([None, self.data.to_numpy().astype(np.float32).shape[1]]))]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        self.data = cast(pd.DataFrame, self.data)
        return {"inputs": self.data.to_numpy().astype(np.float32)[:1]}

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == pd.DataFrame and model_type in [
            OnnxModelType.SKLEARN_ESTIMATOR.value,
            OnnxModelType.XGB_REGRESSOR.value,
            OnnxModelType.LGBM_REGRESSOR.value,
            OnnxModelType.LGBM_CLASSIFIER.value,
            OnnxModelType.STACKING_ESTIMATOR.value,
            OnnxModelType.LGBM_BOOSTER.value,
        ]:
            return True
        return False


class PandasPipelineOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, str]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        return self._get_onnx_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:

        """Converts pandas dataframe associated with SKLearn pipeline or LGB Booster"""

        self.data = cast(pd.DataFrame, self.data)

        inputs = {col: self.data[col].values for col in self.data.columns}

        for col, col_type in zip(self.data.columns, self.data.dtypes):
            if "int32" in str(col_type):
                inputs[col] = inputs[col].astype(np.int32)
            elif "int64" in str(col_type):
                inputs[col] = inputs[col].astype(np.int64)
            elif "float" in str(col_type):
                inputs[col] = inputs[col].astype(np.float32)

        for col in inputs:
            inputs[col] = inputs[col].reshape((self.data.shape[0], 1))

        return inputs

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == pd.DataFrame:
            if model_type == OnnxModelType.SKLEARN_PIPELINE.value:
                return True
        return False


class OnnxDataConverter:
    @staticmethod
    def convert_data(
        input_data: Union[pd.DataFrame, np.ndarray],
        model_type: str,
    ) -> Dict[str, Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        data_type = type(input_data)
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(data_type=data_type, model_type=model_type)
            )
        )

        return converter(data=input_data).convert_data_to_onnx()

    @staticmethod
    def get_data_types(
        input_data: Union[pd.DataFrame, np.ndarray],
        model_type: str,
    ) -> Tuple[List[Any], Optional[Dict[str, str]]]:
        """Takes input data sample and model type and converts data to onnx format"""

        data_type = type(input_data)
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(data_type=data_type, model_type=model_type)
            )
        )

        type_converter = converter(data=input_data)
        onnx_types = type_converter.get_onnx_data_types()
        py_data_types = type_converter.get_data_schema()
        return onnx_types, py_data_types
