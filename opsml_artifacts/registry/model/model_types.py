from opsml_artifacts.registry.model.base_models import OnnxModelType


class ModelType:
    @staticmethod
    def get_type() -> str:
        return "placeholder"

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return True


class SklearnPipeline(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.SKLEARN_PIPELINE.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        if model_class_name == "Pipeline":
            return True
        return False


class SklearnEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.SKLEARN_ESTIMATOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        if model_class_name not in [
            "StackingRegressor",
            "StackingClassifier",
            "Pipeline",
            "LGBMRegressor",
            "XGBRegressor",
        ]:
            return True
        return False


class SklearnStackingEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.STACKING_ESTIMATOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        if model_class_name in ["StackingRegressor", "StackingClassifier"]:
            return True
        return False


class LightGBMRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.LGBM_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        if model_class_name == "LGBMRegressor":
            return True
        return False


class XGBRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return OnnxModelType.XGB_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        if model_class_name == "XGBRegressor":
            return True
        return False
