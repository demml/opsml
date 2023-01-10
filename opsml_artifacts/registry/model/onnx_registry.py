# pylint: disable=import-outside-toplevel
"""Code for generating Onnx Models"""
from pyshipt_logging import ShiptLogging

from opsml_artifacts.registry.model.base_models import OnnxModelType

# Get logger
logger = ShiptLogging.get_logger(__name__)


class RegistryUpdater:
    def update_registry_converter(self):
        pass

    @staticmethod
    def validate(model_estimator: str) -> bool:
        "Validates converter type"

        return True


class LightGBMRegistryUpdater(RegistryUpdater):
    def __init__(self):
        self.alias = "LGBRegressor"

    def update_registry_converter(self):
        logger.info("Registering lightgbm onnx converter")

        from lightgbm import LGBMRegressor
        from onnxmltools.convert.lightgbm.operator_converters.LightGbm import (  # noqa
            convert_lightgbm,
        )
        from skl2onnx import update_registered_converter
        from skl2onnx.common.shape_calculator import (  # noqa
            calculate_linear_regressor_output_shapes,
        )

        update_registered_converter(
            model=LGBMRegressor,
            alias=self.alias,
            shape_fct=calculate_linear_regressor_output_shapes,
            convert_fct=convert_lightgbm,
            overwrite=True,
        )

    @staticmethod
    def validate(model_estimator: str) -> bool:
        if model_estimator == OnnxModelType.LGBM_REGRESSOR.value:
            return True
        return False


class XGBoostRegistryUpdater(RegistryUpdater):
    def __init__(self):
        self.alias = "XGBRegressor"

    def update_registry_converter(self):
        logger.info("Registering xgboost onnx converter")

        from onnxmltools.convert.xgboost.operator_converters.XGBoost import (
            convert_xgboost,
        )
        from skl2onnx import update_registered_converter
        from skl2onnx.common.shape_calculator import (  # noqa
            calculate_linear_regressor_output_shapes,
        )
        from xgboost import XGBRegressor

        update_registered_converter(
            model=XGBRegressor,
            alias=self.alias,
            shape_fct=calculate_linear_regressor_output_shapes,
            convert_fct=convert_xgboost,
            overwrite=True,
        )

    @staticmethod
    def validate(model_estimator: str) -> bool:
        if model_estimator == OnnxModelType.XGB_REGRESSOR.value:
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
            converter().update_registry_converter()
