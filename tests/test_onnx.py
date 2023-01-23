from opsml_artifacts.registry.cards.cards import ModelCard, DataCard
import numpy as np
import pytest
import pandas as pd
from pytest_lazyfixture import lazy_fixture
import timeit


@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("linear_regression"),  # linear regress with dataframe
        lazy_fixture("random_forest_classifier"),  # random forest with numpy
        lazy_fixture("xgb_df_regressor"),  # xgb with dataframe
        lazy_fixture("lgb_booster_dataframe"),  # lgb base package with dataframe
        lazy_fixture("lgb_classifier"),  # lgb classifier with dataframe
        lazy_fixture("sklearn_pipeline"),  # sklearn pipeline with dict onnx input
        lazy_fixture("stacking_regressor"),  # stacking regressor with lgb as one estimator
    ],
)
def test_model_predict(model_and_data):

    model, data = model_and_data

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="test_model",
        team="mlops",
        user_email="test_email",
        data_card_uid="test_uid",
    )

    predictor = model_card.model()

    if isinstance(data, np.ndarray):
        record = {"data": list(np.ravel(data[:1]))}

    elif isinstance(data, pd.DataFrame):
        record = data[0:1].T.to_dict()[0]

    pred_onnx = predictor.predict(record)
    pred_xgb = predictor.predict_with_model(model, record)
    assert pytest.approx(round(pred_onnx, 3)) == round(pred_xgb, 3)


def test_tensorflow(db_registries, load_transformer_example):
    model, data = load_transformer_example

    registry = db_registries["data"]
    data_card = DataCard(
        data=data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)

    model_registry = db_registries["model"]
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="test_model",
        team="mlops",
        user_email="test_email",
        data_card_uid=data_card.uid,
    )

    model_registry.register_card(card=model_card)

    model_card.load_trained_model()
