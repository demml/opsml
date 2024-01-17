# OpsML Model API Example

<img width="450px" src="../../images/fastapi.png" alt="huggingface" class="center" />

The following example shows how you can load a previously registered model and use it to make predictions.

### Workflow

1. (Omitted) - Use `opsml` cli to download model to folder

```bash
opsml-cli download-model --name lightgbm-reg -- version 1.0.0  --onnx
```

2. Configure app with correct information (see `app.py`)

3. Run app

```bash
python app.py
```
