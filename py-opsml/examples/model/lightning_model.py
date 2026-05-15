"""PyTorch Lightning model registration with OpsML."""

from typing import Any

import lightning as L  # type: ignore
import numpy as np
import opsml
import opsml.lightning
import torch  # type: ignore
from opsml import TaskType, start_experiment
from torch import nn
from torch.nn import MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset


class SimpleDataset(Dataset):  # type: ignore
    def __init__(self) -> None:
        x = np.arange(1000)
        self.x = torch.Tensor([[value] for value in x])
        self.y = torch.Tensor([[value * 2] for value in x])

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: Any) -> Any:
        return {"x": self.x[idx], "y": self.y[idx]}


class MyModel(L.LightningModule):
    def __init__(self) -> None:
        super().__init__()
        self.fc = nn.Linear(1, 1)
        self.criterion = MSELoss()

    def forward(self, x, labels=None) -> Any:
        return self.fc(x)

    def train_dataloader(self) -> Any:
        return DataLoader(SimpleDataset(), batch_size=100)

    def training_step(self, batch, batch_idx) -> Any:
        outputs = self(batch["x"])
        return {"loss": self.criterion(outputs, batch["y"])}

    def configure_optimizers(self) -> Any:
        return Adam(self.parameters())


model = MyModel()
trainer = L.Trainer(max_epochs=1, logger=False)
trainer.fit(model)
sample = torch.Tensor([[1.0], [51.0], [89.0]])

with start_experiment(space="examples", name="lightning-quickstart"):
    card = opsml.lightning.log_model(
        trainer,
        name="lightning-regressor",
        sample_data=sample,
        task_type=TaskType.Regression,
    )
    opsml.log_metric("loss", 0.11)
    opsml.log_param("max_epochs", 1)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import LightningModel, ModelCard
# with start_experiment(space="examples", name="lightning-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="lightning-regressor",
#         interface=LightningModel(trainer=trainer, sample_data=sample, task_type=TaskType.Regression),
#     )
#     exp.register_card(card)
