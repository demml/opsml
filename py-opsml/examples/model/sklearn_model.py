"""
Sklearn model registration with OpsML.

Runs in CI via `mise run py:test:examples-model`.
Mirrored in docs/cards/frameworks/sklearn.md via mkdocs snippets.
"""

from typing import Tuple, cast

import opsml
import opsml.sklearn
import pandas as pd
from opsml import TaskType, start_experiment
from opsml.helpers.data import create_fake_data
from sklearn import ensemble  # type: ignore

X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1000))
classifier = ensemble.RandomForestClassifier(n_estimators=10, random_state=42).fit(
    X.to_numpy(),
    y.to_numpy().ravel(),
)

with start_experiment(space="examples", name="sklearn-quickstart"):
    card = opsml.sklearn.log_model(
        classifier,
        name="rf-classifier",
        sample_data=X[:10],
        task_type=TaskType.Classification,
    )
    opsml.log_metric("accuracy", 0.91)
    opsml.log_param("n_estimators", 10)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import ModelCard, SklearnModel
# with start_experiment(space="examples", name="sklearn-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="rf-classifier",
#         interface=SklearnModel(
#             model=classifier,
#             sample_data=X[:10],
#             task_type=TaskType.Classification,
#         ),
#     )
#     exp.register_card(card)
