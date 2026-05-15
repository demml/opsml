"""XGBoost model registration with OpsML."""

from typing import Tuple, cast

import opsml
import opsml.xgboost
import pandas as pd
import xgboost as xgb  # type: ignore
from opsml import TaskType, start_experiment
from opsml.helpers.data import create_fake_data

X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1000))
dtrain = xgb.DMatrix(X.to_numpy(), y.to_numpy())
model = xgb.train({"max_depth": 2, "eta": 1, "objective": "reg:squarederror"}, dtrain, num_boost_round=2)

with start_experiment(space="examples", name="xgboost-quickstart"):
    card = opsml.xgboost.log_model(
        model,
        name="xgb-regressor",
        sample_data=dtrain,
        task_type=TaskType.Regression,
    )
    opsml.log_metric("rmse", 0.31)
    opsml.log_param("num_boost_round", 2)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import ModelCard, XGBoostModel
# with start_experiment(space="examples", name="xgboost-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="xgb-regressor",
#         interface=XGBoostModel(model=model, sample_data=dtrain, task_type=TaskType.Regression),
#     )
#     exp.register_card(card)
