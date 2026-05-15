"""CatBoost model registration with OpsML."""

from typing import Tuple, cast

import catboost  # type: ignore
import opsml
import opsml.catboost
import pandas as pd
from opsml import TaskType, start_experiment
from opsml.helpers.data import create_fake_data

X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1000))
model = catboost.CatBoostClassifier(iterations=5, verbose=False).fit(X.to_numpy(), y.to_numpy().ravel())

with start_experiment(space="examples", name="catboost-quickstart"):
    card = opsml.catboost.log_model(
        model,
        name="catboost-classifier",
        sample_data=X[:10],
        task_type=TaskType.Classification,
    )
    opsml.log_metric("accuracy", 0.9)
    opsml.log_param("iterations", 5)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import CatBoostModel, ModelCard
# with start_experiment(space="examples", name="catboost-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="catboost-classifier",
#         interface=CatBoostModel(model=model, sample_data=X[:10], task_type=TaskType.Classification),
#     )
#     exp.register_card(card)
