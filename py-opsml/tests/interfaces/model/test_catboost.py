from typing import Tuple
from catboost import CatBoostRegressor, CatBoostClassifier, CatBoostRanker  # type: ignore
import pandas as pd
from opsml.model import CatBoostModel, ModelType, ModelLoadKwargs, ModelSaveKwargs
from pathlib import Path


def test_catboost_regressor(
    tmp_path: Path,
    catboost_regressor: Tuple[CatBoostRegressor, pd.DataFrame],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = catboost_regressor

    interface = CatBoostModel(model=model, sample_data=data)

    assert interface.model_type == ModelType.Catboost
    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))
    assert metadata.version != "undefined"

    interface.model = None
    assert interface.model is None

    assert interface.onnx_session is not None
    interface.onnx_session.session = None
    assert interface.onnx_session.session is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None
    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None


def test_catboost_classifier(
    tmp_path: Path,
    catboost_classifier: Tuple[CatBoostClassifier, pd.DataFrame],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = catboost_classifier

    interface = CatBoostModel(model=model, sample_data=data.to_numpy())

    assert interface.model_type == ModelType.Catboost
    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))

    interface.model = None
    assert interface.model is None

    assert interface.onnx_session is not None
    interface.onnx_session.session = None
    assert interface.onnx_session.session is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None
    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None


def test_catboost_ranker(
    tmp_path: Path,
    catboost_ranker: Tuple[CatBoostRanker, pd.DataFrame],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = catboost_ranker

    interface = CatBoostModel(model=model, sample_data=data)

    assert interface.model_type == ModelType.Catboost
    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))

    interface.model = None
    assert interface.model is None

    assert interface.onnx_session is not None
    interface.onnx_session.session = None
    assert interface.onnx_session.session is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None
    assert interface.onnx_session is not None
    assert interface.onnx_session.session is not None
