# pylint: disable=import-outside-toplevel
"""Code for generating Onnx Models"""
from pyshipt_logging import ShiptLogging

from opsml_artifacts.registry.model.types import OnnxModelType

# Get logger
logger = ShiptLogging.get_logger(__name__)


class RegistryUpdater:
    def __init__(self, model_estimator: str):
        self.model_estimator = model_estimator

    def update_registry_converter(self):
        pass

    @staticmethod
    def validate(model_estimator: str) -> bool:
        "Validates converter type"
        raise NotImplementedError


class LightGBMRegistryUpdater(RegistryUpdater):
    def determine_estimator(self) -> str:
        if self.model_estimator == OnnxModelType.LGBM_REGRESSOR:
            return "LGBMRegressor"
        return "LGBMClassifier"

    def get_output_conversion_tools(self):
        from skl2onnx.common.shape_calculator import (
            calculate_linear_classifier_output_shapes,
            calculate_linear_regressor_output_shapes,
        )

        if self.model_estimator == OnnxModelType.LGBM_REGRESSOR:
            return calculate_linear_regressor_output_shapes, None
        return calculate_linear_classifier_output_shapes, {"nocl": [True, False], "zipmap": [True, False, "columns"]}

    def update_registry_converter(self):
        logger.info("Registering lightgbm onnx converter")

        import lightgbm as lgb
        from onnxmltools.convert.lightgbm.operator_converters.LightGbm import (
            convert_lightgbm,
        )
        from skl2onnx import update_registered_converter

        alias = self.determine_estimator()
        output_calculator, options = self.get_output_conversion_tools()
        update_registered_converter(
            model=getattr(lgb, alias),
            alias=alias,
            shape_fct=output_calculator,
            convert_fct=convert_lightgbm,
            overwrite=True,
            options=options,
        )

    @staticmethod
    def validate(model_estimator: str) -> bool:
        if model_estimator in [
            OnnxModelType.LGBM_REGRESSOR,
            OnnxModelType.LGBM_CLASSIFIER,
        ]:
            return True
        return False


class XGBoostRegressorRegistryUpdater(RegistryUpdater):
    def determine_estimator(self) -> str:
        if self.model_estimator == OnnxModelType.XGB_REGRESSOR:
            return "XGBRegressor"
        return "XGBClassifier"

    def get_output_conversion_tools(self):
        from skl2onnx.common.shape_calculator import (
            calculate_linear_classifier_output_shapes,
            calculate_linear_regressor_output_shapes,
        )

        if self.model_estimator == OnnxModelType.XGB_REGRESSOR:
            return calculate_linear_regressor_output_shapes
        return calculate_linear_classifier_output_shapes

    def update_registry_converter(self):
        logger.info("Registering xgboost onnx converter")

        import xgboost as xgb
        from onnxmltools.convert.xgboost.operator_converters.XGBoost import (
            convert_xgboost,
        )
        from skl2onnx import update_registered_converter

        alias = self.determine_estimator()
        output_calculator = self.get_output_conversion_tools()

        update_registered_converter(
            model=getattr(xgb, alias),
            alias=alias,
            shape_fct=output_calculator,
            convert_fct=convert_xgboost,
            overwrite=True,
        )

    @staticmethod
    def validate(model_estimator: str) -> bool:
        if model_estimator == OnnxModelType.XGB_REGRESSOR:
            return True
        return False


class OnnxRegistryUpdater:
    @staticmethod
    def update_onnx_registry(model_estimator_name: str) -> None:
        """Loops through model estimator types and updates
        the Onnx model registry if needed.
        """

        converter = next(
            (
                converter
                for converter in RegistryUpdater.__subclasses__()
                if converter.validate(model_estimator=model_estimator_name)
            ),
            None,
        )

        if converter is not None:
            converter(model_estimator=model_estimator_name).update_registry_converter()
