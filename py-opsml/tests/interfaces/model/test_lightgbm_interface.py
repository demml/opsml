from opsml.model import LightGBMModel, ModelType
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

    interface.save(save_path, True)

    interface.model = None

    assert interface.model is None

    interface.load_model(save_path)

    assert interface.model is not None

    interface.load_onnx_model(save_path)
