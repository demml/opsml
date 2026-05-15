"""ONNX model registration with OpsML."""

from typing import Tuple, cast

import numpy as np
import opsml
import opsml.onnx
import pandas as pd
from opsml import TaskType, start_experiment
from opsml.helpers.data import create_fake_data
from skl2onnx import to_onnx  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore

X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1000))
classifier = RandomForestClassifier(n_estimators=5).fit(X.to_numpy(), y.to_numpy().ravel())
converted_model = to_onnx(classifier, X.to_numpy()[:1].astype(np.float32))

with start_experiment(space="examples", name="onnx-quickstart"):
    card = opsml.onnx.log_model(
        converted_model,
        name="onnx-rf",
        sample_data=X.to_numpy()[:5].astype(np.float32),
        task_type=TaskType.Classification,
    )
    opsml.log_metric("accuracy", 0.89)
    opsml.log_param("n_estimators", 5)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import ModelCard, OnnxModel
# with start_experiment(space="examples", name="onnx-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="onnx-rf",
#         interface=OnnxModel(
#             model=converted_model,
#             sample_data=X.to_numpy()[:5].astype(np.float32),
#             task_type=TaskType.Classification,
#         ),
#     )
#     exp.register_card(card)
