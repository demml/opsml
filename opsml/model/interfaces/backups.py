from typing import Any, Dict

from pydantic import model_validator

from opsml.model.interfaces.base import ModelInterface


class HuggingFaceModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError(
            "HuggingFaceModel requires transformers to be installed. Please install transformers."
        )

    @staticmethod
    def name() -> str:
        return HuggingFaceModelNoModule.__name__


class LightGBMModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("LightGBMModel requires lightgbm to be installed. Please install lightgbm.")

    @staticmethod
    def name() -> str:
        return LightGBMModelNoModule.__name__


class LightningModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError(
            "LightningModel requires pytorch lightning to be installed. Please install lightning."
        )

    @staticmethod
    def name() -> str:
        return LightningModelNoModule.__name__


class TorchModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TorchModel requires torch to be installed. Please install pytorch.")

    @staticmethod
    def name() -> str:
        return TorchModelNoModule.__name__


class SklearnModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("SklearnModel requires scikit-learn to be installed. Please install scikit-learn.")

    @staticmethod
    def name() -> str:
        return SklearnModelNoModule.__name__


class TensorFlowModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("TensorFlowModel requires tensorflow to be installed. Please install tensorflow.")

    @staticmethod
    def name() -> str:
        return TensorFlowModelNoModule.__name__


class XGBoostModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("XGBoostModel requires xgboost to be installed. Please install xgboost.")

    @staticmethod
    def name() -> str:
        return XGBoostModelNoModule.__name__


class CatBoostModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("CatBoost requires catboost to be installed. Please install catboost.")

    @staticmethod
    def name() -> str:
        return CatBoostModelNoModule.__name__


class VowpalWabbitModelNoModule(ModelInterface):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        raise ModuleNotFoundError("VowpalWabbit requires vowpalwabbit to be installed. Please install vowpalwabbit.")

    @staticmethod
    def name() -> str:
        return VowpalWabbitModelNoModule.__name__
