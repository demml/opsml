from typing import Any, Dict

from pydantic import model_validator

from opsml.model.interfaces.base import ModelInterface


class HuggingFaceModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError(
            "HuggingFaceModel requires transformers to be installed. Please install transformers."
        )

    @staticmethod
    def name() -> str:
        return HuggingFaceModel.__name__


class LightGBMModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("LightGBMBoosterModel requires lightgbm to be installed. Please install lightgbm.")

    @staticmethod
    def name() -> str:
        return LightGBMModel.__name__


class LightningModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError(
            "LightningModel requires pytorch lightning to be installed. Please install lightning."
        )

    @staticmethod
    def name() -> str:
        return LightningModel.__name__


class PyTorchModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("PyTorchModel requires torch to be installed. Please install pytorch.")

    @staticmethod
    def name() -> str:
        return PyTorchModel.__name__


class SklearnModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("SklearnModel requires scikit-learn to be installed. Please install scikit-learn.")

    @staticmethod
    def name() -> str:
        return SklearnModel.__name__


class TensorFlowModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TensorFlowModel requires tensorflow to be installed. Please install tensorflow.")

    @staticmethod
    def name() -> str:
        return TensorFlowModel.__name__


class XGBoostModel(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("XGBoostModel requires xgboost to be installed. Please install xgboost.")

    @staticmethod
    def name() -> str:
        return XGBoostModel.__name__
