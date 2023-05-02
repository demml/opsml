import os
from opsml.deploy.seldon import SeldonModel
import pytest


@pytest.mark.parametrize(
    "model_api_path",
    [
        # "linear_reg_model_def.json",
        "random_forest_model_def.json",
    ],
)
def test_seldon(model_api_path):
    os.environ["OPSML_MODELAPI_JSON"] = model_api_path
    seldon = SeldonModel()

    print(seldon.init_metadata())
    a
