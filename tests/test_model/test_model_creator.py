from opsml.model.creator import OnnxModelCreator, ModelCreator
from opsml.registry.data.types import AllowedDataType
import pandas as pd
import pytest


def test_onnx_model_create_fail(iris_data: pd.DataFrame):
    with pytest.raises(Exception) as ve:
        OnnxModelCreator(
            model="Fail",
            input_data=iris_data,
            input_data_type=AllowedDataType.PANDAS,
        ).create_model()

    assert ve.match("Failed to convert model to onnx format.")


def test_model_creator(iris_data: pd.DataFrame):
    with pytest.raises(NotImplementedError):
        ModelCreator(
            model="Fail",
            input_data=iris_data,
            input_data_type=AllowedDataType.PANDAS,
        ).create_model()

    with pytest.raises(NotImplementedError):
        ModelCreator.validate(True)
