import torch
from opsml import (
    CardRegistry,
    ModelCard,
    ModelLoadKwargs,
    ModelSaveKwargs,
    RegistryType,
    TorchModel,
)

registry = CardRegistry(RegistryType.Model)


class Polynomial3(torch.nn.Module):
    def __init__(self):
        """
        In the constructor we instantiate four parameters and assign them as
        member parameters.
        """
        super().__init__()
        self.x1 = torch.nn.Parameter(torch.randn(()))
        self.x2 = torch.nn.Parameter(torch.randn(()))

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        """
        In the forward function we accept a Tensor of input data and we must return
        a Tensor of output data. We can use Modules defined in the constructor as
        well as arbitrary operators on Tensors.
        """
        return self.x1 + self.x2 * x1 * x2


model = Polynomial3()
inputs = {"x1": torch.randn((1, 1)), "x2": torch.randn((1, 1))}

interface = TorchModel(model=model, sample_data=inputs)

modelcard = ModelCard(
    interface=interface,
    space="opsml",
    name="my_model",
)

# Register the model card
registry.register_card(
    card=modelcard,
    save_kwargs=ModelSaveKwargs(save_onnx=True),
)

# List the model card
modelcard_list = registry.list_cards(uid=modelcard.uid).as_table()


# Load the model card
loaded_modelcard: ModelCard = registry.load_card(modelcard.uid)

# Load the model card artifacts
loaded_modelcard.load(
    None,
    load_kwargs=ModelLoadKwargs(
        model={"model": model},
        load_onnx=True,
    ),
)

assert loaded_modelcard.model is not None
assert loaded_modelcard.onnx_session is not None
