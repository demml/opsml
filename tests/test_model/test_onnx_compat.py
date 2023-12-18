import sys
import warnings

import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.registry.cards import ModelCard

EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)


# this is done to filter all the convergence and user warnings during testing
def warn(*args, **kwargs):
    pass


warnings.warn = warn


def model_predict(model_and_data):
    model, data = model_and_data

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uids=["test_uid"],
        to_onnx=True,
    )
    predictor = model_card.onnx_model()

    # if isinstance(data, np.ndarray):
    #    input_name = next(iter(predictor.data_schema.model_data_schema.input_features.keys()))


#
#    record = {input_name: data[0, :].tolist()}
#
# elif isinstance(data, pd.DataFrame):
#    record = list(sample_data[0:1].T.to_dict().values())[0]
#
# else:
#    record = {}
#    for feat, val in sample_data.items():
#        record[feat] = np.ravel(val).tolist()
#
# pred_onnx = predictor.predict(record)
#
# predictor.output_sig(**pred_onnx)
# predictor.predict_with_model(model, record)


@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("huggingface_bart"),
    ],
)
def test_sklearn_models(model_and_data):
    model_predict(model_and_data)
