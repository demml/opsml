from opsml_artifacts.registry.model.types import OnnxModelType


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
        return OnnxModelType.SKLEARN_PIPELINE

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Pipeline"


class SklearnEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.SKLEARN_ESTIMATOR

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
        ]


class SklearnStackingEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.STACKING_ESTIMATOR

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name in ["StackingRegressor", "StackingClassifier"]


class LightGBMRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_REGRESSOR

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMRegressor"


class LightGBMClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_CLASSIFIER

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMClassifier"


class XGBRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.XGB_REGRESSOR

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "XGBRegressor"


class LightGBMBooster(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_BOOSTER

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Booster"


class TensorflowKeras(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.TF_KERAS

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "keras"


class PyTorch(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.PYTORCH

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "pytorch"
