from opsml_artifacts.registry.cards.cards import ModelCard, DataCard
import numpy as np
import pytest
import pandas as pd
from pytest_lazyfixture import lazy_fixture
import timeit


@pytest.mark.parametrize(
    "model_and_data",
    [
        # lazy_fixture("linear_regression"),  # linear regress with numpy
        # lazy_fixture("random_forest_classifier"),  # random forest with numpy
        # lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        # lazy_fixture("lgb_booster_dataframe"),  # lgb base package with dataframe
        # lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        # lazy_fixture("sklearn_pipeline"),  # sklearn pipeline with dict onnx input
        # lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
        # lazy_fixture("load_transformer_example"),
        # lazy_fixture("load_multi_input_keras_example"),
        # lazy_fixture("load_pytorch_resnet"),
        lazy_fixture("load_pytorch_language"),
    ],
)
def _test_model_predict(model_and_data):

    model, data = model_and_data

    print(model)
    print(len(data))
    a

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
        data_card_uids=["test_uid"],
    )

    predictor = model_card.onnx_model()

    if isinstance(data, np.ndarray):
        input_name = next(iter(predictor.data_dict.input_features.keys()))

        record = {input_name: data[0, :].tolist()}

    elif isinstance(data, pd.DataFrame):
        record = data[0:1].T.to_dict()[0]

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
            pred_dict[label] = pred

    out_sig = predictor.output_sig(**pred_dict)
    pred_orig = predictor.predict_with_model(model, record)


@pytest.mark.parametrize(
    "model_and_data",
    [
        # lazy_fixture("linear_regression"),  # linear regress with numpy
        # lazy_fixture("random_forest_classifier"),  # random forest with numpy
        # lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        # lazy_fixture("lgb_booster_dataframe"),  # lgb base package with dataframe
        # lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        # lazy_fixture("sklearn_pipeline"),  # sklearn pipeline with dict onnx input
        # lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
        # lazy_fixture("load_transformer_example"),
        # lazy_fixture("load_multi_input_keras_example"),
        # lazy_fixture("load_pytorch_resnet"),
        lazy_fixture("load_pytorch_language"),
    ],
)
def test_torch_language_model_predict(model_and_data):

    from opsml_artifacts.registry.model.types import TorchOnnxArgs

    model, data = model_and_data

    input_ids, attention_mask = data

    sample_data = {
        "input_ids": input_ids.numpy(),
        "attention_mask": attention_mask.numpy(),
    }

    onnx_args = TorchOnnxArgs(
        input_names=["input_ids", "attention_mask"],
        output_names=["output"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence"},
            "attention_mask": {0: "batch_size", 1: "sequence"},
        },
    )
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=sample_data,
        name="test_model",
        team="mlops",
        user_email="test_email",
        data_card_uids=["test_uid"],
        additional_onnx_args=onnx_args,
    )
    predictor = model_card.onnx_model()
