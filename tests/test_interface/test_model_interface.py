from typing import Tuple

import lightning as L
import pytest

from opsml.data import NumpyData
from opsml.data.interfaces import TorchData
from opsml.model import (
    HuggingFaceModel,
    LightningModel,
    SklearnModel,
    TensorFlowModel,
    TorchModel,
)
from tests.conftest import EXCLUDE


def test_sklearn_interface(linear_regression: Tuple[SklearnModel, NumpyData]) -> None:
    model, _ = linear_regression
    assert model.model_type == "LinearRegression"

    prediction = model.get_sample_prediction()
    assert prediction.prediction_type == "numpy.ndarray"


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_tf_interface(tf_transformer_example: TensorFlowModel) -> None:
    assert tf_transformer_example.model_type == "Functional"
    prediction = tf_transformer_example.get_sample_prediction()
    assert prediction.prediction_type == "numpy.ndarray"


@pytest.mark.flaky(reruns=2, reruns_delay=5)
def test_torch_interface(squeezenet: TorchModel) -> None:
    assert squeezenet.model_type == "SqueezeNet"
    prediction = squeezenet.get_sample_prediction()
    assert prediction.prediction_type == "torch.Tensor"


@pytest.mark.flaky(reruns=1, reruns_delay=2)
@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_lightning_interface(lightning_regression: Tuple[LightningModel, L.LightningModule]) -> None:
    light_model, model = lightning_regression
    assert isinstance(light_model.sample_data, TorchData)
    assert light_model.model_type == "MyModel"
    prediction = light_model.get_sample_prediction()
    assert prediction.prediction_type == "torch.Tensor"


@pytest.mark.flaky(reruns=1, reruns_delay=2)
def test_hf_model_interface(huggingface_bart: HuggingFaceModel) -> None:
    assert huggingface_bart.model_type == "BartModel"
    assert huggingface_bart.model_class == "transformers"
    assert huggingface_bart.task_type == "feature-extraction"
    assert huggingface_bart.backend == "pytorch"

    prediction = huggingface_bart.get_sample_prediction()
    assert prediction.prediction_type == "dict"


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_hf_pipeline_interface(huggingface_text_classification_pipeline: HuggingFaceModel) -> None:
    model = huggingface_text_classification_pipeline
    assert model.model_class == "transformers"
    assert model.task_type == "text-classification"
    assert model.backend == "pytorch"
    assert model.data_type == "str"

    prediction = model.get_sample_prediction()
    assert prediction.prediction_type == "dict"
