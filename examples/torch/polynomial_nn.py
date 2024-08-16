# Example taken from https://pytorch.org/tutorials/beginner/examples_nn/two_layer_net_module.html

from typing import Any

import torch

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class Polynomial3(torch.nn.Module):
    def __init__(self) -> None:
        """
        In the constructor we instantiate four parameters and assign them as
        member parameters.
        """
        super().__init__()
        self.a = torch.nn.Parameter(torch.randn(()))
        self.b = torch.nn.Parameter(torch.randn(()))
        self.c = torch.nn.Parameter(torch.randn(()))
        self.d = torch.nn.Parameter(torch.randn(()))

    def forward(self, x) -> Any:
        """
        In the forward function we accept a Tensor of input data and we must return
        a Tensor of output data. We can use Modules defined in the constructor as
        well as arbitrary operators on Tensors.
        """
        return self.a + self.b * x + self.c * x**2 + self.d * x**3

    def string(self) -> str:
        """
        Just like any class in Python, you can also define custom method on PyTorch modules
        """
        return f"y = {self.a.item()} + {self.b.item()} x + {self.c.item()} x^2 + {self.d.item()} x^3"

    def train_model(self, x: torch.Tensor, y: torch.Tensor) -> None:
        """Training logic for Polynomial3 model

        Args:
            x:
                Training features
            y:
                Training label

        """
        criterion = torch.nn.MSELoss(reduction="sum")
        optimizer = torch.optim.SGD(self.parameters(), lr=1e-6)

        logger.info("Starting model training")
        for t in range(2000):
            # Forward pass: Compute predicted y by passing x to the model
            y_pred = self(x)

            # Compute and print loss
            loss = criterion(y_pred, y)
            if t % 100 == 99:
                print(t, loss.item())

            # Zero gradients, perform a backward pass, and update the weights.
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        logger.info("Model training complete")
