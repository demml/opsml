import lightning as L
import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset


class SimpleDataset(Dataset):
    def __init__(self, X: torch.Tensor, y: torch.Tensor):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return {"X": self.X[idx], "y": self.y[idx]}


class RegressionModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(1, 1)
        self.criterion = nn.MSELoss()
        self._dataset = None

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        self._dataset = dataset

    def forward(self, inputs_id, labels=None):
        outputs = self.fc(inputs_id)
        return outputs

    def train_dataloader(self):
        return DataLoader(self.dataset, batch_size=1000)

    def training_step(self, batch, batch_idx):
        input_ids = batch["X"]
        labels = batch["y"]

        outputs = self(input_ids, labels)
        loss = 0
        if labels is not None:
            loss = self.criterion(outputs, labels)
        return {"loss": loss}

    def configure_optimizers(self):
        optimizer = Adam(self.parameters())
        return optimizer
