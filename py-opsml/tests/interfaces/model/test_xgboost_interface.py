from opsml.model import XGBoostModel, ModelType, ModelLoadKwargs, ModelSaveKwargs
import xgboost as xgb
from typing import Tuple
from pathlib import Path
from sklearn.preprocessing import StandardScaler  # type: ignore


def test_xgboost_model_interface(
    tmp_path: Path,
    xgb_booster_regressor_model: Tuple[xgb.Booster, xgb.DMatrix, StandardScaler],
):
    save_path = tmp_path / "test"
    save_path.mkdir()

    model, data, scaler = xgb_booster_regressor_model

    interface = XGBoostModel(model=model, sample_data=data, preprocessor=scaler)

    assert interface.model_type == ModelType.XgbBooster

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
