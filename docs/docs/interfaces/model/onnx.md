# Onnx Args

Some model interfaces require extra arguments when converting to onnx. These arguments can be passed to the `onnx_args` argument of the `ModelInterface` class.

## TorchOnnxArgs

`TorchOnnxArgs` is the optional onnx args class for `TorchModel` and `LightningModel`. When not supplied, a default `TorchOnnxArgs` class is used. For more information on the arguments, please refer to the [torch.onnx](https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html) documentation.


::: opsml.TorchOnnxArgs
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3

---
## HuggingFaceOnnxArgs

`HuggingFaceOnnxArgs` is the **REQUIRED** onnx args class for `HuggingFaceModel` when converting a model to onnx format. `HuggingFaceOnnxArgs` is a custom object that allows you to specify how [`optimum`](https://github.com/huggingface/optimum) should convert your model to onnx. 

### Required Arguments

`ort_type`
: Optimum onnx class name as defined in [`HuggingFaceORTModel`](./extras.md#huggingfaceortmodel)

`provider`
: Onnx runtime provider to user. Defaults to `CPUExecutionProvider`

`quantize`
: Whether or not to quantize the model. Defaults to `False`. If `True` a `quantization` config is required.

`config`
: Optional config for conversion. Can be one of `AutoQuantizationConfig`, `ORTConfig` or `QuantizationConfig`. See [`optimum`](https://github.com/huggingface/optimum) for more details.

::: opsml.HuggingFaceOnnxArgs
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3