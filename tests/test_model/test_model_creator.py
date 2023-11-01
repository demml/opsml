from opsml.model.creator import OnnxModelCreator
import pytest


def test_onnx_model_create_fail(iris_data):
    with pytest.raises(Exception) as ve:
        OnnxModelCreator(
            model="Fail",
            input_data=iris_data,
        ).create_model()

    assert ve.match("Failed to convert model to onnx format.")
