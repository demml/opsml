from opsml.model import TorchModel, LoadKwargs
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

    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None

    print(interface.onnx_session.session)

    interface.model = None
    interface.onnx_session.session = None

    print(interface.onnx_session.session)

    assert interface.model is None
    assert interface.onnx_session.session is None

    interface.load(
        save_path,
        model=True,
        onnx=True,
        sample_data=True,
        load_kwargs=LoadKwargs(model={"model": model}),
    )

    assert interface.model is not None
    assert interface.onnx_session is not None

    interface.model(**data)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def _test_pytorch_simple_tuple(
    tmp_path: Path, pytorch_simple_tuple: Tuple[torch.nn.Module, dict]
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = pytorch_simple_tuple
    interface = TorchModel(model=model, sample_data=data)

    assert isinstance(interface.sample_data, tuple)
    assert interface.data_type == DataType.Tuple

    metadata = interface.save(save_path, True)

    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None

    interface.model = None
    interface.onnx_session = None
    assert interface.model is None
    assert interface.onnx_session is None

    print(metadata)

    interface.load(save_path, model=True, onnx=True, sample_data=True)

    assert interface.model is not None

    interface.model(*data)
