import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture
import numpy as np
from opsml_artifacts.registry.cards.card import DataCard, ExperimentCard
from opsml_artifacts.registry.sql.registry import CardRegistry
from opsml_artifacts.registry.cards.creator import ModelCardCreator
import timeit


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_arrow_table")),
    ],
)
def test_register_data(setup_data_registry, test_data, storage_client, data_splits):

    # create data card
    registry: CardRegistry = setup_data_registry
    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )

    registry.register_card(card=data_card)

    df = registry.list_cards(name=data_card.name, team=data_card.team)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(name=data_card.name)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards()
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=data_card.data_uri)


def test_experiment_card(linear_regression, setup_experiment_registry):

    experiment_registry: CardRegistry = setup_experiment_registry

    experiment = ExperimentCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_card_uid="test_uid",
    )

    experiment.add_metric("test_metric", 10)
    experiment.add_metrics({"test_metric2": 20})
    assert experiment.metrics.get("test_metric") == 10
    assert experiment.metrics.get("test_metric2") == 20

    # save artifacts
    model, _ = linear_regression

    experiment.add_artifact("reg_model", artifact=model)
    assert experiment.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"

    experiment_registry.register_card(card=experiment)
    loaded_exp = experiment_registry.load_card(uid=experiment.uid)
    assert loaded_exp.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"


# def _test_register_base_model(setup_model_registry, model_list, storage_client):
#
#    registry: CardRegistry = setup_model_registry
#    models, data = model_list
#
#    for model in models:
#        model_creator = ModelCardCreator(model=model, input_data=data)
#        model_card = model_creator.create_model_card(
#            model_name="test_model",
#            team="mlops",
#            user_email="test_email",
#            registered_data_uid="test_uid",
#        )
#
#        registry.register_card(card=model_card)
#        storage_client.delete_object_from_url(gcs_uri=model_card.model_uri)


@pytest.mark.parametrize("data_card_uid", ["test_uid"])
def test_register_pipeline_model(
    setup_model_registry, setup_data_registry, sklearn_pipeline, storage_client, data_card_uid
):

    model, data = sklearn_pipeline

    # create data card
    data_registry: CardRegistry = setup_data_registry
    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)
    model_registry: CardRegistry = setup_model_registry

    for data_card_id in [data_card.uid, None, "test_uid"]:
        model_creator = ModelCardCreator(model=model, input_data=data)
        model_card = model_creator.create_model_card(
            model_name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            registered_data_uid=data_card_id,
        )

        if data_card_id != data_card.uid:
            with pytest.raises(ValueError):
                model_registry.register_card(card=model_card)

        else:
            model_registry.register_card(card=model_card)
            storage_client.delete_object_from_url(gcs_uri=model_card.model_uri)


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits(test_data):

    data_split = [
        {"label": "train", "column": "year", "column_value": 2020},
        {"label": "test", "column": "year", "column_value": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits[0]["column"] == "year"
    assert data_card.data_splits[0]["column_value"] == 2020

    data_split = [
        {"label": "train", "start": 0, "stop": 2},
        {"label": "test", "start": 3, "stop": 4},
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits[0]["start"] == 0
    assert data_card.data_splits[0]["stop"] == 2


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_load_data_card(setup_data_registry, test_data, storage_client):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry: CardRegistry = setup_data_registry

    data_split = [
        {"label": "train", "column": "year", "column_value": 2020},
        {"label": "test", "column": "year", "column_value": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        name=data_name,
        team=team,
        user_email=user_email,
        data_splits=data_split,
    )

    registry.register_card(card=data_card)
    loaded_data = registry.load_card(name=data_name, team=team, version=data_card.version)

    # update
    loaded_data.version = 100

    registry.update_card(card=loaded_data)
    storage_client.delete_object_from_url(gcs_uri=loaded_data.data_uri)

    df = registry.list_cards(name=data_name, team=team, version=100)

    assert df["version"].to_numpy()[0] == 100


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
def _test_model_predict(model_and_data):

    model, data = model_and_data
    model_creator = ModelCardCreator(model=model, input_data=data)
    model_card = model_creator.create_model_card(
        model_name="test_model",
        team="mlops",
        user_email="test_email",
        registered_data_uid="test_uid",
    )

    predictor = model_card.model()

    if isinstance(data, np.ndarray):
        record = {"data": list(np.ravel(data[:1]))}

    elif isinstance(data, pd.DataFrame):
        record = data[0:1].T.to_dict()[0]

    pred_onnx = predictor.predict(record)
    pred_xgb = predictor.predict_with_model(model, record)
    assert pytest.approx(round(pred_onnx, 3)) == round(pred_xgb, 3)

    # test1 = timeit.Timer(lambda: predictor.predict(record)).timeit(1000)
    # test2 = timeit.Timer(lambda: predictor.predict_with_model(model, record)).timeit(1000)
    # print(f"onnx: {test1}, sklearn: {test2}")
    # a
