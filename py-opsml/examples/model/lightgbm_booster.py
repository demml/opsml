"""LightGBM model registration with OpsML."""

from typing import Tuple, cast

import lightgbm as lgb  # type: ignore
import opsml
import opsml.lightgbm
import pandas as pd
from opsml import TaskType, start_experiment
from opsml.helpers.data import create_fake_data

X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1000))
dataset = lgb.Dataset(X.to_numpy(), y.to_numpy().ravel())
model = lgb.train(
    {"objective": "binary", "verbosity": -1},
    dataset,
    num_boost_round=5,
)

with start_experiment(space="examples", name="lightgbm-quickstart"):
    card = opsml.lightgbm.log_model(
        model,
        name="lgb-classifier",
        sample_data=dataset,
        task_type=TaskType.Classification,
    )
    opsml.log_metric("accuracy", 0.9)
    opsml.log_param("n_estimators", 5)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import LightGBMModel, ModelCard
# with start_experiment(space="examples", name="lightgbm-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="lgb-classifier",
#         interface=LightGBMModel(model=model, sample_data=dataset, task_type=TaskType.Classification),
#     )
#     exp.register_card(card)
