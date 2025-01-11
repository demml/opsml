from typing import Tuple
from opsml.model import SklearnModel
from opsml.data import NumpyData


def test_linear_regression_numpy(linear_regression: Tuple[SklearnModel, NumpyData]):
    model, _ = linear_regression
    model.convert_to_onnx()
    a
