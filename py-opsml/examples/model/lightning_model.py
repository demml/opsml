from typing import Any

import lightning as L  # type: ignore
import numpy as np
import torch
from opsml import (
    CardRegistry,
    LightningModel,
    ModelCard,
    ModelLoadKwargs,
    ModelSaveKwargs,
    RegistryType,
)
from torch import nn
from torch.nn import MSELoss
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset

registry = CardRegistry(RegistryType.Model)


class SimpleDataset(Dataset):  # type: ignore
    def __init__(self) -> None:
        X = np.arange(10000)
        y = X * 2
        X = [[_] for _ in X]  # type: ignore
        y = [[_] for _ in y]  # type: ignore
        self.X = torch.Tensor(X)
        self.y = torch.Tensor(y)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: Any) -> Any:
        return {"X": self.X[idx], "y": self.y[idx]}


class MyModel(L.LightningModule):
    def __init__(self) -> None:
        super().__init__()
        self.fc = nn.Linear(1, 1)
        self.criterion = MSELoss()

    def forward(self, inputs_id, labels=None) -> Any:
        outputs = self.fc(inputs_id)
        return outputs

    def train_dataloader(self) -> Any:
        dataset = SimpleDataset()
        return DataLoader(dataset, batch_size=1000)

    def training_step(self, batch, batch_idx) -> Any:
        input_ids = batch["X"]
        labels = batch["y"]
        outputs = self(input_ids, labels)
        loss = 0
        if labels is not None:
            loss = self.criterion(outputs, labels)
        return {"loss": loss}

    def configure_optimizers(self) -> Any:
        optimizer = Adam(self.parameters())
        return optimizer


model = MyModel()
trainer = L.Trainer(max_epochs=1)
trainer.fit(model)

X = torch.Tensor([[1.0], [51.0], [89.0]])

interface = LightningModel(trainer=trainer, sample_data=X)

modelcard = ModelCard(
    interface=interface,
    space="opsml",
    name="my_model",
)

# Register the model card
registry.register_card(
    modelcard,
    save_kwargs=ModelSaveKwargs(save_onnx=True),  # convert to onnx
)

# List the model card
modelcard_list = registry.list_cards(uid=modelcard.uid).as_table()


# Load the model card
loaded_modelcard: ModelCard = registry.load_card(modelcard.uid)

# Load the model card artifacts
loaded_modelcard.load(
    None,
    load_kwargs=ModelLoadKwargs(
        model={"model": MyModel},
        load_onnx=True,
    ),
)

assert loaded_modelcard.model is not None
assert loaded_modelcard.onnx_session is not None
