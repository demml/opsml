from opsml.registry.cards.cards import ModelCard
import numpy as np
import pytest
import pandas as pd
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    "model_and_data",
    [
        # lazy_fixture("linear_regression"),  # linear regress with numpy
        lazy_fixture("random_forest_classifier"),  # random forest with dataframe
        # lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        # lazy_fixture("lgb_booster_dataframe"),  # lgb base package with dataframe
        # lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        # lazy_fixture("sklearn_pipeline"),  # sklearn pipeline with dict onnx input
        # lazy_fixture("sklearn_pipeline_advanced"),
        # lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
        # lazy_fixture("load_transformer_example"),  # keras transformer example
        # lazy_fixture("load_multi_input_keras_example"),  # keras multi input model
        # lazy_fixture("load_pytorch_resnet"),  # pytorch resent trained with numpy array
        # lazy_fixture("load_pytorch_language"),  # huggingface automodel "distil-bert" trained with dictionary
    ],
)
def test_model_predict(model_and_data):

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

    with open("random_fores_model_def.json", "w") as file_:
        file_.write(predictor.get_api_model().json())

    if isinstance(data, np.ndarray):
        input_name = next(iter(predictor.data_dict.input_features.keys()))

        record = {input_name: data[0, :].tolist()}

    elif isinstance(data, pd.DataFrame):
        record = list(sample_data[0:1].T.to_dict().values())[0]

    else:
        record = {}
        for feat, val in sample_data.items():
            record[feat] = np.ravel(val).tolist()

    pred_onnx = predictor.predict(record)

    #
    ## test output sig
    pred_dict = {}
    for label, pred in zip(predictor._output_names, pred_onnx):
        if predictor.model_type in ["keras", "pytorch"]:
            pred_dict[label] = np.ravel(pred).tolist()

        else:
            if isinstance(pred, list):
                pred_dict[label] = pred
            else:
                pred_dict[label] = list(pred.flatten())

    out_sig = predictor.output_sig(**pred_dict)
    pred_orig = predictor.predict_with_model(model, record)
