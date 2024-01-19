# Model Extras

In addition to interface and onnx-related objects, there are a few objects that may be of use when interactions with models. 

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
## OnnxModel

OnnxModel is a pydantic class that is used to store converted onnx models. In the case of a BYO onnx model, you will need to supply an `OnnxModel` object to the `ModelInterface` class.

```python hl_lines="2  13-16 22"
from opsml import SklearnModel, ModelCard
from opsml.types import OnnxModel
import onnx

# you decide to convert your sklearn model to onnx manually

# onnx conversion logic
...

# create interface
interface = SklearnModel(
    model=model,
    onnx_model=OnnxModel(
        onnx_version=onnx.__version__,
        sess=ort_session, # this should be an onnxruntime.InferenceSession object
        ),
    )

ModelCard(
    interface=interface, 
    info=info, 
    to_onnx=True, # opsml will detect the custom `OnnxModel` and handle it accordingly
)
```

::: opsml.types.OnnxModel
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3