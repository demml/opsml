from opsml.deploy.loader import ModelLoader, Model
import os
import pytest


@pytest.mark.parametrize(
    "model_api_path",
    [
        "linear-reg-model-metadata.json",
        "random-forest-classifier-model-metadata.json",
    ],
)
def test_model(model_api_path):
    os.environ["OPSML_MODEL_METADATA_JSON"] = model_api_path
    models = ModelLoader().model_files
    loader = Model(model_path=models[0])

    assert len(models) == 1


def test_models():
    os.environ.pop("OPSML_MODEL_METADATA_JSON")
    models = ModelLoader().model_files
    assert len(models) == 4
