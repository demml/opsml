## HuggingFace Example

<img width="450px" src="../../images/huggingface.png" alt="huggingface" class="center" />

The following examples demonstrates how to use Opsml with `HuggingFace`.

### Workflow

1. Creates fake text dataset
2. Creates a `DataCard` with a TextDataset
3. Fine-tune `HuggingFace` model, save to `ModelCard` with onnx conversion and quantization.
4. Load `ModelCard` and test onnx model
