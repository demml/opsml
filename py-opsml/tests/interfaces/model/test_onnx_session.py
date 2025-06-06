from typing import Tuple
import warnings
from pathlib import Path
from opsml.model import (
    SklearnModel,
    OnnxSession,
    ModelInterfaceMetadata,
    ModelSaveKwargs,
)
from opsml.data import NumpyData


def warn(*args, **kwargs):
    pass


warnings.warn = warn


def test_onnx_session(
    tmp_path: Path, linear_regression: Tuple[SklearnModel, NumpyData]
):
    model, _ = linear_regression
    metadata = model.save(tmp_path, ModelSaveKwargs(save_onnx=True))
    assert model.onnx_session is not None
    model.onnx_session.run({"X": model.sample_data.data}, None)  # type: ignore

    onnx_json = model.onnx_session.model_dump_json()

    loaded_sess = OnnxSession.model_validate_json(onnx_json)
    assert loaded_sess is not None
    assert loaded_sess.session is None
    assert loaded_sess.schema == model.onnx_session.schema

    meta_json = metadata.model_dump_json()

    loaded_metadata = ModelInterfaceMetadata.model_validate_json(meta_json)

    assert metadata.onnx_session is not None
    assert loaded_metadata.onnx_session is not None

    assert metadata.onnx_session.schema == loaded_metadata.onnx_session.schema
