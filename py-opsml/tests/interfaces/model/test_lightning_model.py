from opsml.model import LightningModel, ModelLoadKwargs, ModelSaveKwargs
from opsml.types import DataType
import lightning as L
import torch
from pathlib import Path
import pytest
from typing import Tuple, Any
import sys
import platform

WINDOWS_EXCLUDE = sys.platform == "win32"
DARWIN_EXCLUDE = sys.platform == "darwin" and platform.machine() == "arm64"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_lightning_model(
    tmp_path: Path, pytorch_lightning_model: Tuple[L.Trainer, torch.Tensor]
):
    trainer, data = pytorch_lightning_model

    interface = LightningModel(trainer=trainer, sample_data=data)

    assert interface.data_type == DataType.TorchTensor


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_lightning_regression(
    tmp_path: Path, lightning_regression: Tuple[LightningModel, Any]
):
    interface, model = lightning_regression

    assert interface.data_type == DataType.TorchTensor

    save_path = tmp_path / "test"
    save_path.mkdir()

    assert interface.onnx_session is None
    assert interface.model is None
    assert interface.trainer is not None

    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))
    assert metadata.version != "undefined"

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(
            model={"model": model},
            load_onnx=True,
        ),
    )


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_lightning_classification(
    tmp_path: Path, lightning_classification: Tuple[LightningModel, Any]
):
    interface, model = lightning_classification

    assert interface.data_type == DataType.TorchTensor

    save_path = tmp_path / "test"
    save_path.mkdir()

    assert interface.onnx_session is None
    assert interface.model is None
    assert interface.trainer is not None

    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(
            model={"model": model},
            load_onnx=True,
        ),
    )
