from opsml.deploy.loader import ModelLoader, Model
import os
import pytest


@pytest.mark.parametrize(
    "model_api_path",
    [
        "linear_regression_model_def.json",
        "random_forest_classifier_model_def.json",
    ],
)
def test_model(model_api_path):

    os.environ["OPSML_MODELAPI_JSON"] = model_api_path
    models = ModelLoader().model_files
    loader = Model(model_path=models[0])

    assert len(models) == 1


def test_models():
    os.environ.pop("OPSML_MODELAPI_JSON")
    models = ModelLoader().model_files
    assert len(models) == 2
