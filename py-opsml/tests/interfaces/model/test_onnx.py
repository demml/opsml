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
    a
