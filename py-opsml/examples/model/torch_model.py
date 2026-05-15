"""PyTorch model registration with OpsML."""

import opsml
import opsml.torch
import torch  # type: ignore
from opsml import TaskType, start_experiment

model = torch.nn.Linear(4, 1)
sample = torch.rand(10, 4)

with start_experiment(space="examples", name="torch-quickstart"):
    card = opsml.torch.log_model(
        model,
        name="torch-linear",
        sample_data=sample,
        task_type=TaskType.Regression,
    )
    opsml.log_metric("loss", 0.12)
    opsml.log_param("in_features", 4)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import ModelCard, TorchModel
# with start_experiment(space="examples", name="torch-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="torch-linear",
#         interface=TorchModel(model=model, sample_data=sample, task_type=TaskType.Regression),
#     )
#     exp.register_card(card)
