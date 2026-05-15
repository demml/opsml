"""TensorFlow model registration with OpsML."""

import numpy as np
import opsml
import opsml.tensorflow
import tensorflow as tf  # type: ignore
from opsml import TaskType, start_experiment

model = tf.keras.Sequential(
    [
        tf.keras.layers.Input(shape=(4,)),
        tf.keras.layers.Dense(1),
    ]
)
sample = np.random.rand(10, 4)

with start_experiment(space="examples", name="tensorflow-quickstart"):
    card = opsml.tensorflow.log_model(
        model,
        name="tf-dense",
        sample_data=sample,
        task_type=TaskType.Regression,
    )
    opsml.log_metric("loss", 0.14)
    opsml.log_param("layers", 1)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import ModelCard, TensorFlowModel
# with start_experiment(space="examples", name="tensorflow-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="tf-dense",
#         interface=TensorFlowModel(model=model, sample_data=sample, task_type=TaskType.Regression),
#     )
#     exp.register_card(card)
