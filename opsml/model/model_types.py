# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from opsml.model.types import OnnxModelType


class ModelType:
    @staticmethod
    def get_type() -> str:
        raise NotImplementedError

    @staticmethod
    def validate(model_class_name: str) -> bool:
        raise NotImplementedError


class SklearnPipeline(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.SKLEARN_PIPELINE.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Pipeline"


class SklearnEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.SKLEARN_ESTIMATOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name not in [
            "StackingRegressor",
            "StackingClassifier",
            "Pipeline",
            "LGBMRegressor",
            "LGBMClassifier",
            "XGBRegressor",
            "Booster",
            "keras",
            "pytorch",
            "transformer",
            "CalibratedClassifierCV",
        ]


class SklearnCalibratedClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.CALIBRATED_CLASSIFIER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "CalibratedClassifierCV"


class SklearnStackingEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.STACKING_ESTIMATOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name in ["StackingRegressor", "StackingClassifier"]


class LightGBMRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMRegressor"


class LightGBMClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_CLASSIFIER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMClassifier"


class XGBRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.XGB_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "XGBRegressor"


class LightGBMBooster(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_BOOSTER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Booster"


class TensorflowKeras(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.TF_KERAS.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "keras"


class PyTorch(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.PYTORCH.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "pytorch"


class Transformer(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.TRANSFORMER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "transformer"
