import sys
from typing import Tuple

import pytest

from opsml.data import NumpyData
from opsml.model import (
    HuggingFaceModel,
    LightningModel,
    SklearnModel,
    TensorFlowModel,
    TorchModel,
)

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_sklearn_interface(linear_regression: Tuple[SklearnModel, NumpyData]):
    model, _ = linear_regression
    assert model.model_type == "LinearRegression"

    prediction = model.get_sample_prediction()
    assert prediction.prediction_type == "numpy.ndarray"


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_tf_interface(tf_transformer_example: TensorFlowModel):
    assert tf_transformer_example.model_type == "Functional"
    prediction = tf_transformer_example.get_sample_prediction()
    assert prediction.prediction_type == "numpy.ndarray"


@pytest.mark.flaky(reruns=2, reruns_delay=5)
@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_torch_interface(deeplabv3_resnet50: TorchModel):
    assert deeplabv3_resnet50.model_type == "DeepLabV3"
    prediction = deeplabv3_resnet50.get_sample_prediction()
    assert prediction.prediction_type == "collections.OrderedDict"


@pytest.mark.flaky(reruns=1, reruns_delay=2)
@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_lightning_interface(lightning_regression: LightningModel):

    light_model, model = lightning_regression
    assert light_model.model_type == "MyModel"
    prediction = light_model.get_sample_prediction()
    assert prediction.prediction_type == "torch.Tensor"


@pytest.mark.flaky(reruns=1, reruns_delay=2)
@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_hf_model_interface(huggingface_bart: HuggingFaceModel):

    assert huggingface_bart.model_type == "BartModel"
    assert huggingface_bart.model_class == "transformers"
    assert huggingface_bart.task_type == "feature-extraction"
    assert huggingface_bart.backend == "pytorch"

    prediction = huggingface_bart.get_sample_prediction()
    assert prediction.prediction_type == "dict"


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_hf_pipeline_interface(huggingface_text_classification_pipeline: HuggingFaceModel):
    model = huggingface_text_classification_pipeline
    assert model.model_class == "transformers"
    assert model.task_type == "text-classification"
    assert model.backend == "pytorch"
    assert model.data_type == "str"

    prediction = model.get_sample_prediction()
    assert prediction.prediction_type == "dict"
