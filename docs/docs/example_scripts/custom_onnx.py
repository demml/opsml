# Some standard imports
import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8888/"


import tempfile

from torch import nn
import torch.utils.model_zoo as model_zoo
import torch.onnx
import onnx

# Super Resolution model definition in PyTorch
import torch.nn as nn
import torch.nn.init as init


## opsml
from opsml.model.types import OnnxModelDefinition
from opsml.registry import CardRegistries, ModelCard, DataCard

registries = CardRegistries()


class SuperResolutionNet(nn.Module):
    def __init__(self, upscale_factor, inplace=False):
        super(SuperResolutionNet, self).__init__()

        self.relu = nn.ReLU(inplace=inplace)
        self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
        self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
        self.conv3 = nn.Conv2d(64, 32, (3, 3), (1, 1), (1, 1))
        self.conv4 = nn.Conv2d(32, upscale_factor**2, (3, 3), (1, 1), (1, 1))
        self.pixel_shuffle = nn.PixelShuffle(upscale_factor)

        self._initialize_weights()

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.pixel_shuffle(self.conv4(x))
        return x

    def _initialize_weights(self):
        init.orthogonal_(self.conv1.weight, init.calculate_gain("relu"))
        init.orthogonal_(self.conv2.weight, init.calculate_gain("relu"))
        init.orthogonal_(self.conv3.weight, init.calculate_gain("relu"))
        init.orthogonal_(self.conv4.weight)


# Create the super-resolution model by using the above model definition.
torch_model = SuperResolutionNet(upscale_factor=3)

# Load pretrained model weights
model_url = "https://s3.amazonaws.com/pytorch/test_data/export/superres_epoch100-44c6958e.pth"
batch_size = 1  # just a random number

# Initialize model with the pretrained weights
map_location = lambda storage, loc: storage
if torch.cuda.is_available():
    map_location = None
torch_model.load_state_dict(model_zoo.load_url(model_url, map_location=map_location))

# set the model to inference mode
torch_model.eval()

# Input to the model
x = torch.randn(batch_size, 1, 224, 224, requires_grad=True)
torch_out = torch_model(x)

# Export the model
with tempfile.TemporaryDirectory() as tmpdir:
    onnx_path = f"{tmpdir}/super_resolution.onnx"
    torch.onnx.export(
        torch_model,  # model being run
        x,  # model input (or a tuple for multiple inputs)
        onnx_path,  # where to save the model (can be a file or file-like object)
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=10,  # the ONNX version to export the model to
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names=["input"],  # the model's input names
        output_names=["output"],  # the model's output names
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},  # variable length axes
    )

    onnx_model = onnx.load(onnx_path)


######## Create DataCard
datacard = DataCard(
    name="image-data",
    team="opsml",
    user_email="user@opsml.com",
    data=x.detach().numpy(),
)
registries.data.register_card(datacard)


####### Create ModelCard

model_def = OnnxModelDefinition(
    onnx_version="1.14.0",
    model_bytes=onnx_model.SerializeToString(),
)

ModelCard(
    name="pytorch-custom-onnx",
    team="opmsl",
    user_email="opsml.com",
    trained_model=torch_model,
    sample_input_data=x.numpy()[0:1],
    onnx_model_def=model_def,
)
registries.model.register_card(datacard)
