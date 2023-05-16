import os
from opsml.deploy.seldon import SeldonModel
from pytest_lazyfixture import lazy_fixture
import pytest
import math


@pytest.mark.parametrize(
    "model_api_path, api_example",
    [
        ("linear-reg-model-metadata.json", lazy_fixture("linear_reg_api_example")),
        ("random-forest-classifier-model-metadata.json", lazy_fixture("random_forest_api_example")),
        ("tensorflow-multi-model-metadata.json", lazy_fixture("tensorflow_api_example")),
        ("sklearn-pipeline-model-metadata.json", lazy_fixture("sklearn_pipeline_api_example")),
    ],
)
def test_seldon(model_api_path, api_example):
    expected_value, example = api_example

    os.environ["OPSML_MODEL_METADATA_JSON"] = model_api_path
    seldon = SeldonModel()
    seldon.init_metadata()

    prediction = seldon.predict_raw(request=example)

    for output_name in ["variable", "output_label", "priority"]:
        output = prediction.get(output_name)

        if output is not None:
            if isinstance(expected_value, dict):
                assert math.isclose(output, expected_value.get(output_name), abs_tol=0.01)
            else:
                assert math.isclose(output, expected_value, abs_tol=0.01)
