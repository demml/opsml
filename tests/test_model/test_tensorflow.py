import sys

from opsml.registry.cards import ModelCard, ModelCardMetadata
import numpy as np
import pytest
import pandas as pd
from pytest_lazyfixture import lazy_fixture
import warnings


# this is done to filter all the convergence and user warnings during testing
def warn(*args, **kwargs):
    pass


warnings.warn = warn


def model_predict(model_and_data):
    model, data = model_and_data

    if isinstance(data, dict):
        sample_data = data
    else:
        sample_data = data[0:1]

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
    )
    predictor = model_card.onnx_model()

    if isinstance(data, np.ndarray):
        input_name = next(iter(predictor.data_schema.model_data_schema.input_features.keys()))

        record = {input_name: data[0, :].tolist()}

    elif isinstance(data, pd.DataFrame):
        record = list(sample_data[0:1].T.to_dict().values())[0]

    else:
        record = {}
        for feat, val in sample_data.items():
            record[feat] = np.ravel(val).tolist()

    pred_onnx = predictor.predict(record)

    out_sig = predictor.output_sig(**pred_onnx)
    pred_orig = predictor.predict_with_model(model, record)


@pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on apple silicon")
@pytest.mark.skipif(sys.platform == "win32", reason="No tf test with wn_32")
@pytest.mark.parametrize(
    "model_and_data",
    [
        # Not supported on apple silicon
        lazy_fixture("load_transformer_example"),  # keras transformer example
        lazy_fixture("load_multi_input_keras_example"),  # keras multi input model
    ],
)
def test_tensorflow_predict(model_and_data):
    model_predict(model_and_data)
    a
