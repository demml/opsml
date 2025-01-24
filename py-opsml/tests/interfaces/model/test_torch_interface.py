from opsml.model import TorchModel
from opsml.data import DataType
from typing import Tuple
import torch
from pathlib import Path
import pytest
import sys

WINDOWS_EXCLUDE = sys.platform == "win32"


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pytorch_simple(tmp_path: Path, pytorch_simple: Tuple[torch.nn.Module, dict]):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = pytorch_simple
    interface = TorchModel(model=model, sample_data=data)

    assert isinstance(interface.sample_data, dict)
    assert interface.data_type == DataType.Dict

    interface.save(save_path, True)

    interface.model = None

    assert interface.model is None

    interface.load_model(save_path, model)

    assert interface.model is not None

    interface.model(**data)

    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pytorch_simple_tuple(
    tmp_path: Path, pytorch_simple_tuple: Tuple[torch.nn.Module, dict]
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = pytorch_simple_tuple
    interface = TorchModel(model=model, sample_data=data)

    assert isinstance(interface.sample_data, tuple)
    assert interface.data_type == DataType.Tuple

    interface.save(save_path, True)

    interface.model = None

    assert interface.model is None

    interface.load_model(save_path, model)

    assert interface.model is not None

    interface.model(*data)

    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None
