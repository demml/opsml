# type: ignore
import warnings

import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.model import (
    HuggingFaceModel,
    LightningModel,
    TorchModel,
)
from tests import conftest
from tests.conftest import EXCLUDE


# this is done to filter all the convergence and user warnings during testing
def warn(*args, **kwargs):
    pass


warnings.warn = warn


@pytest.mark.flaky(reruns=2, reruns_delay=2)
@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("pytorch_resnet"),  # resnet
        lazy_fixture("squeezenet"),  # squeezenet
    ],
)
def test_model_pytorch_predict(interface: TorchModel):
    interface.convert_to_onnx()
    assert interface.onnx_model.sess is not None


@pytest.mark.flaky(reruns=2, reruns_delay=2)
@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("huggingface_torch_distilbert"),  # huggingface sequence classifier
        lazy_fixture("huggingface_text_classification_pipeline"),
    ],
)
def test_huggingface_model(interface: HuggingFaceModel):
    interface.convert_to_onnx()
    assert interface.onnx_model.sess is not None


@pytest.mark.flaky(reruns=2)
@pytest.mark.skipif(EXCLUDE, reason="Not supported")
@pytest.mark.parametrize(
    "interface",
    [
        lazy_fixture("lightning_regression"),  # pytorch lightning
    ],
)
def test_torch_lightning_predict(interface: LightningModel) -> None:
    interface, _ = interface
    interface.convert_to_onnx()
    assert interface.onnx_model.sess is not None

    # clean up lightning logs
    conftest.cleanup()
