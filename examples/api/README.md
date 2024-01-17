# OpsML Model API Example

<img width="450px" src="../../images/fastapi.png" alt="huggingface" class="center" />

The following example shows how you can load a previously registered model and use it to make predictions.

### Workflow

1. (Omitted) - Use `opsml` cli to download model to folder

```bash
opsml-cli download-model --name lightgbm-reg -- version 1.0.0  --onnx
```

2. Configure app with correct information (see `app.py`)

- `api/app.py` - contains FastAPI application
- `api/core/models.py` - contains request, response, and model loading logic (makes use of `ModelLoader` class)
- `api/core/config.py` - contains api configuration information
- `api/core/lifespan_handler.py` - contains startup and shutdown logic
- `api/core/routes.py` - contains `healthcheck` and `predict` endpoints
- `api/model` - directory containing downloaded model artifacts


3. Run app

```bash
python app.py
```
