import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml_artifacts.registry.cards.cards import DataCard, ExperimentCard, PipelineCard, ModelCard
from opsml_artifacts.registry.cards.pipeline_loader import PipelineLoader
from opsml_artifacts.registry.sql.registry import CardRegistry
import uuid
import random
from pydantic import ValidationError
from unittest.mock import patch, MagicMock


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_arrow_table")),
    ],
)
def test_register_data(db_registries, test_data, data_splits, mock_pyarrow_parquet_write):

    # create data card
    registry = db_registries["data"]
    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )

    # for numpy array
    with patch.multiple("zarr", save=MagicMock(return_value=None)):
        registry.register_card(card=data_card)

        df = registry.list_cards(name=data_card.name, team=data_card.team)
        assert isinstance(df, pd.DataFrame)

        df = registry.list_cards(name=data_card.name)
        assert isinstance(df, pd.DataFrame)

        df = registry.list_cards()
        assert isinstance(df, pd.DataFrame)


def test_experiment_card(linear_regression, db_registries):
    with patch.multiple(
        "joblib",
        dump=MagicMock(return_value=None),
        load=MagicMock(return_value=linear_regression),
    ):
        registry: CardRegistry = db_registries["experiment"]
        experiment = ExperimentCard(
            name="test_df",
            team="mlops",
            user_email="mlops.com",
            data_card_uids=["test_uid"],
        )
        experiment.add_metric("test_metric", 10)
        experiment.add_metrics({"test_metric2": 20})
        assert experiment.metrics.get("test_metric") == 10
        assert experiment.metrics.get("test_metric2") == 20
        # save artifacts
        model, _ = linear_regression
        experiment.add_artifact("reg_model", artifact=model)
        assert experiment.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"
        registry.register_card(card=experiment)
        loaded_card = registry.load_card(uid=experiment.uid)
        assert loaded_card.uid == experiment.uid


@patch("opsml_artifacts.registry.cards.cards.ModelCard.load_trained_model")
@patch("opsml_artifacts.registry.sql.records.LoadedModelRecord.load_model_card_definition")
def test_register_model(
    loaded_model_record, model_card_mock, db_registries, sklearn_pipeline, mock_pyarrow_parquet_write
):

    model_card_mock.return_value = None
    model, data = sklearn_pipeline
    # create data card
    data_registry: CardRegistry = db_registries["data"]

    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)

    model_card1 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        data_card_uid=data_card.uid,
    )

    with patch.multiple(
        "joblib",
        dump=MagicMock(return_value=None),
        load=MagicMock(return_value=model_card1.dict(exclude={"sample_input_data", "trained_model"})),
    ):

        model_registry: CardRegistry = db_registries["model"]
        model_registry.register_card(model_card1)

        loaded_model_record.return_value = model_card1.dict()
        loaded_card = model_registry.load_card(uid=model_card1.uid)
        loaded_card.load_trained_model()
        loaded_card.trained_model = model
        loaded_card.sample_input_data = data[0:1]

    assert getattr(loaded_card, "trained_model") is not None
    assert getattr(loaded_card, "sample_input_data") is not None

    model_card2 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        data_card_uid=None,
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card2)

    model_card3 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        data_card_uid="test_uid",
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card3)

    with pytest.raises(ValidationError):
        model_card3 = ModelCard(
            trained_model=model,
            sample_input_data=None,
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid="test_uid",
        )


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
def test_load_data_card(db_registries, test_data, mock_pyarrow_parquet_write, mock_pyarrow_parquet_dataset):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry: CardRegistry = db_registries["data"]

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
        additional_info={"input_metadata": 20},
        dependent_vars=[200, "test"],
    )

    data_card.add_info(info={"added_metadata": 10})
    registry.register_card(card=data_card)
    loaded_data: DataCard = registry.load_card(name=data_name, team=team, version=data_card.version)

    loaded_data.load_data()

    assert int(loaded_data.additional_info["input_metadata"]) == 20
    assert int(loaded_data.additional_info["added_metadata"]) == 10
    assert isinstance(loaded_data.dependent_vars[0], int)
    assert isinstance(loaded_data.dependent_vars[1], str)
    assert bool(loaded_data)

    # update
    loaded_data.version = "1.2.0"
    registry.update_card(card=loaded_data)

    record = registry.query_value_from_card(uid=loaded_data.uid, columns=["version", "timestamp"])
    assert record["version"] == "1.2.0"

    # test assertion error
    with pytest.raises(ValueError):
        data_card = DataCard(
            name=data_name,
            team=team,
            user_email=user_email,
            data_splits=data_split,
            additional_info={"input_metadata": 20},
            dependent_vars=[200, "test"],
        )


def test_pipeline_registry(db_registries, mock_pyarrow_parquet_write):
    pipeline_card = PipelineCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        pipeline_code_uri="test_pipe_uri",
    )
    for card_type in ["data", "data", "model", "experiment"]:
        pipeline_card.add_card_uid(
            uid=uuid.uuid4().hex,
            card_type=card_type,
            name=f"{card_type}_{random.randint(0,100)}",
        )
    # register
    registry: CardRegistry = db_registries["pipeline"]
    registry.register_card(card=pipeline_card)
    loaded_card: PipelineCard = registry.load_card(uid=pipeline_card.uid)
    loaded_card.add_card_uid(uid="updated_uid", card_type="data", name="update")
    registry.update_card(card=loaded_card)
    df = registry.list_cards(uid=loaded_card.uid)
    values = registry.query_value_from_card(
        uid=loaded_card.uid,
        columns=["data_card_uids"],
    )
    assert values["data_card_uids"].get("update") == "updated_uid"


def test_full_pipeline_with_loading(db_registries, linear_regression, mock_pyarrow_parquet_write):
    team = "mlops"
    user_email = "mlops.com"
    pipeline_code_uri = "test_pipe_uri"
    data_registry: CardRegistry = db_registries["data"]
    model_registry: CardRegistry = db_registries["model"]
    experiment_registry: CardRegistry = db_registries["experiment"]
    pipeline_registry: CardRegistry = db_registries["pipeline"]
    local_client = db_registries["connection_client"]
    model, data = linear_regression
    #### Create DataCard
    data_card = DataCard(
        data=data,
        name="test_data",
        team=team,
        user_email=user_email,
    )
    with patch.multiple("zarr", save=MagicMock(return_value=None)):
        data_registry.register_card(card=data_card)
        ###### ModelCard
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[:1],
            name="test_model",
            team=team,
            user_email=user_email,
            data_card_uid=data_card.uid,
        )
        with patch.multiple("joblib", dump=MagicMock(return_value=None)):
            model_registry.register_card(model_card)

    ##### ExperimentCard
    exp_card = ExperimentCard(
        name="test_experiment",
        team=team,
        user_email=user_email,
        data_card_uids=[data_card.uid],
        model_card_uids=[model_card.uid],
    )
    exp_card.add_metric("test_metric", 10)
    experiment_registry.register_card(card=exp_card)
    #### PipelineCard
    pipeline_card = PipelineCard(
        name="test_pipeline",
        team=team,
        user_email=user_email,
        pipeline_code_uri=pipeline_code_uri,
        data_card_uids={"data1": data_card.uid},
        model_card_uids={"model1": model_card.uid},
        experiment_card_uids={"exp1": exp_card.uid},
    )
    pipeline_registry.register_card(card=pipeline_card)
    with patch(
        "opsml_artifacts.registry.cards.pipeline_loader.PipelineLoader._load_cards",
        return_value=None,
    ):
        loader = PipelineLoader(pipeline_card_uid=pipeline_card.uid)
        with patch.object(loader, "_card_deck", {"data1": data_card, "model1": model_card, "exp1": exp_card}):
            deck = loader.load_cards()
            uids = loader.card_uids
            assert all(name in deck.keys() for name in ["data1", "exp1", "model1"])
            assert all(name in uids.keys() for name in ["data1", "exp1", "model1"])
            loader.visualize()
