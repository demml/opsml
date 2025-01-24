from opsml.model import TorchModel, SaveKwargs
from opsml.data import DataType
from typing import Tuple
import torch
from pathlib import Path


def test_pytorch_simple(tmp_path: Path, pytorch_simple: Tuple[torch.nn.Module, dict]):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = pytorch_simple
    interface = TorchModel(model=model, sample_data=data)

    assert isinstance(interface.sample_data, dict)
    assert interface.data_type == DataType.Dict

    interface.save(save_path, False)

    interface.model = None

    assert interface.model is None

    interface.load_model(save_path, model)

    assert interface.model is not None

    interface.model(**data)
