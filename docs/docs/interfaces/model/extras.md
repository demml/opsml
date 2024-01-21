# Model Extras

In addition to interface and onnx-related objects, there are a few objects that may be of use when interactions with models. 

---
## HuggingFaceORTModel

The `HuggingFaceORTModel` is an enum that allows you to specify an ORT type for a `HuggingFaceModel`. Refer to the source code below for the available options.

```python
from opsml import HuggingFaceORTModel, HuggingFaceOnnxArgs

HuggingFaceOnnxArgs(
    ort_type=HuggingFaceORTModel.ORT_SEQUENCE_CLASSIFICATION.value,
    provider="CPUExecutionProvider",
    quantize=False,
    )
```

::: opsml.HuggingFaceORTModel
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3


---
## HuggingFaceTask

HuggingFaceTask is an enum that allows you to specify a task type for a `HuggingFaceModel`. Refer to the source code below for the available options.

```python
from opsml import HuggingFaceTask, HuggingFaceModel

HuggingFaceModel(
    model=model,
    task_type=HuggingFaceTask.SEQUENCE_CLASSIFICATION.value,
    )
```

::: opsml.HuggingFaceTask
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3



---
## TorchSaveArgs

Optional `TorchModel` arguments for saving a `TorchModel` object. Only `as_state_dict` is currently supported. If True, the `TorchModel` model object's state dict will be

::: opsml.types.TorchSaveArgs
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3



---
## OnnxModel

OnnxModel is a pydantic class that is used to store converted onnx models. In the case of a BYO onnx model, you will need to supply an `OnnxModel` object to the `ModelInterface` class.


```python hl_lines="79"
from opsml import OnnxModel, TorchModel
import onnx
import onnxruntime as ort

# Super Resolution model definition in PyTorch
import torch.nn as nn
import torch.nn.init as init
import torch.onnx
import torch.utils.model_zoo as model_zoo
from torch import nn

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
def map_location(storage, loc):
    return storage

if torch.cuda.is_available():
    map_location = None
torch_model.load_state_dict(model_zoo.load_url(model_url, map_location=map_location))

# set the model to inference mode
torch_model.eval()

# Input to the model
x = torch.randn(batch_size, 1, 224, 224, requires_grad=True)
torch_model(x)

with tempfile.TemporaryDirectory() as tmpdir:
    onnx_path = f"{tmpdir}/super_resolution.onnx"
    # Export the model
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

    ort_sess = ort.InferenceSession(onnx_model.SerializeToString())

onnx_model = OnnxModel(onnx_version="1.14.0", sess=ort_sess)

interface = TorchModel(
    model=torch_model,
    sample_data=x,
    onnx_model=onnx_model,
    save_args={"as_state_dict": True},
)
```

::: opsml.types.OnnxModel
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3