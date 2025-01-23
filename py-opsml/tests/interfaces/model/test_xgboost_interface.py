from opsml.model import XGBoostModel, ModelType
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

    interface.save(save_path, False)


# interface.model = None

# assert interface.model is None

# interface.load_model(save_path)

# assert interface.model is not None

# interface.load_onnx_model(save_path)
