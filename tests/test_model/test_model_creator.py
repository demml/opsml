from opsml.model.creator import OnnxModelCreator, ModelCreator
import pytest


def test_onnx_model_create_fail(iris_data):
    with pytest.raises(Exception) as ve:
        OnnxModelCreator(
            model="Fail",
            input_data=iris_data,
        ).create_model()

    assert ve.match("Failed to convert model to onnx format.")


def test_model_creator(iris_data):
    with pytest.raises(NotImplementedError):
        ModelCreator(
            model="Fail",
            input_data=iris_data,
        ).create_model()

    with pytest.raises(NotImplementedError):
        ModelCreator.validate(True)
