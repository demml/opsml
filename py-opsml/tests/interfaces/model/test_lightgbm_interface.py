from opsml.model import (
    LightGBMModel,
    ModelType,
    ModelSaveKwargs,
    SklearnModel,
    ModelLoadKwargs,
)
import lightgbm as lgb
import pandas as pd
from typing import Tuple
from pathlib import Path


def test_lightgbm_model_interface(
    tmp_path: Path, lgb_booster_model: Tuple[lgb.Booster, pd.DataFrame]
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data = lgb_booster_model

    interface = LightGBMModel(model=model, sample_data=data)

    assert interface.model_type == ModelType.LgbmBooster

    metadata = interface.save(save_path, ModelSaveKwargs(save_onnx=True))
    assert metadata.version != "undefined"

    interface.model = None
    assert interface.model is None

    interface.load(
        save_path,
        metadata.save_metadata,
        load_kwargs=ModelLoadKwargs(load_onnx=True),
    )

    assert interface.model is not None
    assert interface.onnx_session is not None


def test_lightgbm_regression_metadata(
    tmp_path: Path, lightgbm_regression: SklearnModel
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    save_kwargs = ModelSaveKwargs(
        onnx={"target_opset": {"ai.onnx.ml": 3, "": 9}},
        save_onnx=True,
    )

    assert lightgbm_regression.model_type == ModelType.LgbmRegressor

    lightgbm_regression.save(save_path, save_kwargs)
