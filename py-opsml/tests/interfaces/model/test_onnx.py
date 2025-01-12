from typing import Tuple
from opsml.core import OpsmlLogger, LogLevel
from opsml.model import SklearnModel
from opsml.data import NumpyData, PandasData

OpsmlLogger.setup_logging(LogLevel.Debug)


def test_linear_regression_numpy(linear_regression: Tuple[SklearnModel, NumpyData]):
    model, _ = linear_regression
    model.convert_to_onnx()


def test_random_forest_classifier(random_forest_classifier: SklearnModel):
    model = random_forest_classifier
    model.convert_to_onnx()


def test_sklearn_pipeline(sklearn_pipeline: Tuple[SklearnModel, PandasData]):
    model, _ = sklearn_pipeline
    model.convert_to_onnx()


def test_lgb_classifier_calibrated(lgb_classifier_calibrated: SklearnModel):
    model = lgb_classifier_calibrated
    model.convert_to_onnx()


def test_sklearn_pipeline_advanced(sklearn_pipeline_advanced: SklearnModel):
    model = sklearn_pipeline_advanced
    model.convert_to_onnx()


def test_stacking_regressor(stacking_regressor: SklearnModel):
    model = stacking_regressor
    model.convert_to_onnx()


def test_sklearn_pipeline_xgb_classifier(sklearn_pipeline_xgb_classifier: SklearnModel):
    model = sklearn_pipeline_xgb_classifier
    model.convert_to_onnx()
