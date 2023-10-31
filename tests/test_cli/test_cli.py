from typing import Tuple
from typer.testing import CliRunner
from sklearn import linear_model
import pandas as pd
from opsml.registry import DataCard, ModelCard, CardRegistries, RunCard, CardInfo, ModelCardMetadata
import tempfile
from opsml.cli.api_cli import app
from sklearn import pipeline


runner = CliRunner()


def test_download_model(
    api_registries: CardRegistries,
    mock_cli_property,
    linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame],
):
    team = "mlops"
    user_email = "mlops.com"

    model, data = linear_regression

    data_registry = api_registries.data
    model_registry = api_registries.model

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

    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["download-model", "--name", "test_model", "--team", team, "--write-dir", tmpdirname]
        )
        assert result.exit_code == 0


def test_download_model_metadata(
    api_registries: CardRegistries,
    mock_cli_property,
    linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame],
):
    team = "mlops"
    user_email = "mlops.com"

    model, data = linear_regression

    data_registry = api_registries.data
    model_registry = api_registries.model

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

    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["download-model-metadata", "--name", "test_model", "--team", team, "--write-dir", tmpdirname]
        )
        assert result.exit_code == 0


def test_list_cards(
    api_registries: CardRegistries,
    mock_cli_property,
    linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame],
):
    team = "mlops"
    user_email = "mlops.com"

    model, data = linear_regression

    data_registry = api_registries.data
    model_registry = api_registries.model

    #### Create DataCard
    data_card = DataCard(
        data=data,
        name="test_data",
        team=team,
        user_email=user_email,
        tags={"test": "data"},
    )

    data_registry.register_card(card=data_card)

    result = runner.invoke(app, ["list-cards", "--registry", "data", "--name", "test_model", "--team", team])
    assert result.exit_code == 0

    # test tag
    result = runner.invoke(
        app,
        [
            "list-cards",
            "--registry",
            "data",
            "--name",
            "test_model",
            "--team",
            team,
            "--tag-key",
            "test",
            "--tag-value",
            "data",
        ],
    )

    assert result.exit_code == 0


def test_launch_server(mock_typer):
    result = runner.invoke(app, ["launch-server"])


def test_launch_uvicorn(mock_opsml_app_run):
    result = runner.invoke(app, ["launch-uvicorn-app"])
    assert result.exit_code == 0


def test_model_metrics(
    api_registries: CardRegistries,
    mock_cli_property,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    model, data = sklearn_pipeline
    card_info = CardInfo(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
    )

    runcard = RunCard(info=card_info)

    runcard.log_metric(key="mae", value=2)
    runcard.log_metric(key="mape", value=2, step=1)
    runcard.log_metric(key="mape", value=2, step=2)
    runcard.log_parameter(key="m1", value="apple")
    api_registries.run.register_card(runcard)

    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    api_registries.data.register_card(datacard)

    #### Create ModelCard
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=card_info,
        datacard_uid=datacard.uid,
        metadata=ModelCardMetadata(runcard_uid=runcard.uid),
    )
    api_registries.model.register_card(modelcard)

    result = runner.invoke(app, ["get-model-metrics", "--uid", modelcard.uid])
    assert result.exit_code == 0

    # test metric failure
    result = runner.invoke(app, ["get-model-metrics", "--name", modelcard.name, "--team", modelcard.team])
    assert result.exit_code == 1

    ### Create 2nd batch
    runcard = RunCard(info=card_info)
    runcard.log_metric(key="mae", value=10)
    runcard.log_metric(key="mape", value=2, step=1)
    runcard.log_metric(key="mape", value=2, step=2)
    runcard.log_parameter(key="m1", value="apple")
    api_registries.run.register_card(runcard)

    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    api_registries.data.register_card(datacard)

    #### Create ModelCard
    challenger = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=card_info,
        datacard_uid=datacard.uid,
        metadata=ModelCardMetadata(runcard_uid=runcard.uid),
    )
    api_registries.model.register_card(challenger)

    # test compare metrics
    result = runner.invoke(
        app,
        [
            "compare-model-metrics",
            "--challenger-uid",
            challenger.uid,
            "--champion-uid",
            modelcard.uid,
            "--metric-name",
            "mae",
        ],
    )

    assert result.exit_code == 0


def test_download_data_profile(
    api_registries: CardRegistries,
    mock_cli_property,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    _, data = sklearn_pipeline
    card_info = CardInfo(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
    )

    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    datacard.create_data_profile()
    api_registries.data.register_card(datacard)
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(app, ["download-data-profile", "--uid", datacard.uid, "--write-dir", tmpdirname])

    assert result.exit_code == 0

    # failure
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["download-data-profile", "--name", datacard.name, "--team", datacard.team, "--write-dir", tmpdirname]
        )

    assert result.exit_code == 1


def test_compare_data_profile(
    api_registries: CardRegistries,
    mock_cli_property,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    _, data = sklearn_pipeline
    card_info = CardInfo(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
    )

    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    datacard.create_data_profile()
    api_registries.data.register_card(datacard)

    # test uids
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["compare-data-profiles", "--uid", datacard.uid, "--uid", datacard.uid, "--write-dir", tmpdirname]
        )

    assert result.exit_code == 0

    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app,
            [
                "compare-data-profiles",
                "--name",
                datacard.name,
                "--version",
                datacard.version,
                "--version",
                datacard.version,
                "--write-dir",
                tmpdirname,
            ],
        )
    assert result.exit_code == 0

    # failure
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["compare-data-profiles", "--name", datacard.name, "--team", datacard.team, "--write-dir", tmpdirname]
        )
    assert result.exit_code == 1

    # Not data profile fail
    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    api_registries.data.register_card(datacard)

    # failure
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app,
            [
                "compare-data-profiles",
                "--name",
                datacard.name,
                "--team",
                datacard.team,
                "--version",
                datacard.version,
                "--version",
                datacard.version,
                "--write-dir",
                tmpdirname,
            ],
        )

    assert result.exit_code == 1

    # failure
    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app,
            [
                "compare-data-profiles",
                "--uid",
                datacard.uid,
                "--uid",
                datacard.uid,
                "--write-dir",
                tmpdirname,
            ],
        )

    assert result.exit_code == 1
