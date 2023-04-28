import pandas as pd
from os import path
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.cards.cards import DataCard, RunCard, PipelineCard, ModelCard
from opsml.registry.cards.pipeline_loader import PipelineLoader
from opsml.registry.sql.registry import CardRegistry
import uuid
from pydantic import ValidationError
import pytest


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_arrow_table")),
    ],
)
def test_register_data(db_registries, test_data, data_splits):

    # create data card
    registry = db_registries["data"]
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

    df = registry.list_cards(name=data_card.name, team=data_card.team, version="1.0.0")
    assert df.shape[0] == 1


def test_datacard_sql(db_registries, test_array):

    # create data card
    registry = db_registries["data"]
    data_card = DataCard(
        data=test_array,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    name = "test"
    query = "select * from test_table"
    data_card.add_sql(name=name, query=query)

    assert data_card.sql_logic[name] == query

    name = "test"
    filename = "test_sql.sql"
    data_card.add_sql(name=name, filename=filename)

    assert data_card.sql_logic[name] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"

    ### Test add failure
    with pytest.raises(ValueError):
        data_card.add_sql(name="fail", filename="fail.sql")

    with pytest.raises(ValueError):
        data_card.add_sql(name="fail")

    ## Test instantiation
    data_card = DataCard(data=test_array, name="test_df", team="mlops", user_email="mlops.com", sql_logic={name: query})
    assert data_card.sql_logic[name] == query

    data_card = DataCard(
        data=test_array, name="test_df", team="mlops", user_email="mlops.com", sql_logic={name: filename}
    )
    assert data_card.sql_logic[name] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"

    ## Test instantiation failure
    with pytest.raises(ValueError):
        data_card = DataCard(
            data=test_array, name="test_df", team="mlops", user_email="mlops.com", sql_logic={"fail": "fail.sql"}
        )


def test_semver_registry_list(db_registries, test_array):

    # create data card
    registry = db_registries["data"]

    # version 1
    for i in range(0, 5):
        data_card = DataCard(
            data=test_array,
            name="test_df",
            team="mlops",
            user_email="mlops.com",
        )
        registry.register_card(card=data_card)

    # version 2
    data_card = DataCard(
        data=test_array,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )
    registry.register_card(card=data_card, version_type="major")

    for i in range(0, 12):
        data_card = DataCard(
            data=test_array,
            name="test_df",
            team="mlops",
            user_email="mlops.com",
        )
        registry.register_card(card=data_card)

    # should return 13 versions
    df = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="2.*.*",
    )
    assert df.shape[0] == 13

    df = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="^2.3.0",
    )
    assert df.shape[0] == 13

    df = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="~2.3.0",
    )
    assert df.shape[0] == 1

    # should return
    card = registry.load_card(
        name=data_card.name,
        team=data_card.team,
        version="^2.3.0",
    )

    assert card.version == "2.12.0"

    df = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="^2.3.0",
        limit=1,
    )
    assert df.shape[0] == 1


def test_runcard(linear_regression, db_registries):

    registry: CardRegistry = db_registries["run"]
    run = RunCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        datacard_uids=["test_uid"],
    )
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10
    assert run.get_metric("test_metric2").value == 20

    # save artifacts
    model, _ = linear_regression
    run.log_artifact("reg_model", artifact=model)
    assert run.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"
    registry.register_card(card=run)
    loaded_card = registry.load_card(uid=run.uid)
    assert loaded_card.uid == run.uid
    assert loaded_card.get_metric("test_metric").value == 10
    assert loaded_card.get_metric("test_metric2").value == 20

    with pytest.raises(ValueError):
        loaded_card.get_metric("test")

    with pytest.raises(ValueError):
        loaded_card.get_param("test")

    # metrics take floats, ints
    with pytest.raises(ValueError):
        loaded_card.log_metric("test_fail", "10")

    # params take floats, ints, str
    with pytest.raises(ValueError):
        loaded_card.log_param("test_fail", model)

    # test updating
    loaded_card.log_metric("updated_metric", 20)
    registry.update_card(card=loaded_card)

    # should be same runid
    loaded_card = registry.load_card(uid=run.uid)
    assert loaded_card.get_metric("updated_metric").value == 20
    assert loaded_card.runcard_uri == run.runcard_uri


def test_local_model_registry(db_registries, sklearn_pipeline):

    # create data card
    data_registry: CardRegistry = db_registries["data"]
    model, data = sklearn_pipeline
    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
    )

    with pytest.raises(ValueError):
        model_card.load_onnx_model_definition()

    with pytest.raises(ValueError):
        model_card.load_trained_model()

    model_registry: CardRegistry = db_registries["model"]
    model_registry.register_card(model_card)

    assert path.exists(model_card.onnx_model_uri)
    assert path.exists(model_card.trained_model_uri)
    assert path.exists(model_card.sample_data_uri)

    loaded_card = model_registry.load_card(uid=model_card.uid)

    assert loaded_card != model_card
    assert loaded_card.onnx_model_def is None
    assert loaded_card.trained_model is None
    assert loaded_card.sample_input_data is None

    loaded_card.load_onnx_model_definition()
    loaded_card.load_trained_model()

    assert loaded_card.trained_model is not None
    assert loaded_card.sample_input_data is not None
    assert loaded_card.onnx_model_def is not None

    with pytest.raises(ValueError):
        model_registry.update_card(loaded_card)


def test_register_model(db_registries, sklearn_pipeline):

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
        datacard_uid=data_card.uid,
    )

    model_registry: CardRegistry = db_registries["model"]
    model_registry.register_card(model_card1)

    loaded_card = model_registry.load_card(uid=model_card1.uid)
    loaded_card.load_trained_model()

    loaded_card.trained_model = model
    loaded_card.sample_input_data = data[0:1]

    assert getattr(loaded_card, "trained_model") is not None
    assert getattr(loaded_card, "sample_input_data") is not None

    model_card_custom = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
    )

    model_registry.register_card(card=model_card_custom, save_path="steven-test/models")
    assert "steven-test/models" in model_card_custom.trained_model_uri

    model_card2 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=None,
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card2)

    model_card3 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid="test_uid",
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
            datacard_uid="test_uid",
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
def test_load_data_card(db_registries, test_data):
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
        sql_logic={"test": "SELECT * FROM TEST_TABLE"},
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
    assert loaded_data.sql_logic["test"] == "SELECT * FROM TEST_TABLE"

    assert loaded_data.data_splits == data_split

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


def test_pipeline_registry(db_registries):
    pipeline_card = PipelineCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        pipeline_code_uri="test_pipe_uri",
    )
    for card_type in ["data", "run", "model"]:
        pipeline_card.add_card_uid(uid=uuid.uuid4().hex, card_type=card_type)

    # register
    registry: CardRegistry = db_registries["pipeline"]
    registry.register_card(card=pipeline_card)
    loaded_card: PipelineCard = registry.load_card(uid=pipeline_card.uid)
    loaded_card.add_card_uid(uid="updated_uid", card_type="data")
    registry.update_card(card=loaded_card)
    df = registry.list_cards(uid=loaded_card.uid)
    values = registry.query_value_from_card(
        uid=loaded_card.uid,
        columns=["datacard_uids"],
    )
    assert bool(values["datacard_uids"])


def test_full_pipeline_with_loading(db_registries, linear_regression):

    team = "mlops"
    user_email = "mlops.com"
    pipeline_code_uri = "test_pipe_uri"
    data_registry: CardRegistry = db_registries["data"]
    model_registry: CardRegistry = db_registries["model"]
    experiment_registry: CardRegistry = db_registries["run"]
    pipeline_registry: CardRegistry = db_registries["pipeline"]
    model, data = linear_regression

    #### Create DataCard
    data_card = DataCard(
        data=data,
        name="test_data",
        team=team,
        user_email=user_email,
    )

    data_registry.register_card(card=data_card)
    ###### ModelCard
    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[:1],
        name="test_model",
        team=team,
        user_email=user_email,
        datacard_uid=data_card.uid,
    )

    model_registry.register_card(model_card)

    ##### RunCard
    exp_card = RunCard(
        name="test_experiment",
        team=team,
        user_email=user_email,
        datacard_uids=[data_card.uid],
        modelcard_uids=[model_card.uid],
    )
    exp_card.log_metric("test_metric", 10)
    experiment_registry.register_card(card=exp_card)

    #### PipelineCard
    pipeline_card = PipelineCard(
        name="test_pipeline",
        team=team,
        user_email=user_email,
        pipeline_code_uri=pipeline_code_uri,
        datacard_uids=[data_card.uid],
        modelcard_uids=[model_card.uid],
        runcard_uids=[exp_card.uid],
    )
    pipeline_registry.register_card(card=pipeline_card)

    loader = PipelineLoader(pipelinecard_uid=pipeline_card.uid)
    uids = loader.card_uids

    assert uids["data"][0] == data_card.uid
    assert uids["run"][0] == exp_card.uid
    assert uids["model"][0] == model_card.uid


def _test_tensorflow(db_registries, load_transformer_example, mock_pathlib):

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
        datacard_uid=data_card.uid,
    )

    model_registry.register_card(card=model_card)
    model_card.load_trained_model()
