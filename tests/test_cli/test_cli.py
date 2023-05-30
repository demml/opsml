from typing import Tuple, cast
from typer.testing import CliRunner
from sklearn import linear_model
import pandas as pd
from opsml.registry import DataCard, ModelCard, CardRegistries
import tempfile
from opsml.cli.api_cli import app
from opsml.projects.mlflow import MlflowProject, ProjectInfo, MlflowActiveRun
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
    )

    data_registry.register_card(card=data_card)

    result = runner.invoke(app, ["list-cards", "--registry", "data", "--name", "test_model", "--team", team])
    print(result.__dict__)
    assert result.exit_code == 0


def _test_launch_server(test_app, api_registries, linear_regression):
    result = runner.invoke(app, ["launch-server"])
    assert result.exit_code == 0


def test_model_metrics(
    mlflow_project: MlflowProject, mock_cli_property, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")

    with mlflow_project.run() as run:
        # Create metrics / params / cards
        run = cast(MlflowActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_metric(key="mape", value=2, step=1)
        run.log_metric(key="mape", value=2, step=2)
        run.log_parameter(key="m1", value="apple")
        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card, version_type="major")
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
        )
        run.register_card(card=model_card)
        info.run_id = run.run_id

    result = runner.invoke(app, ["get-model-metrics", "--uid", model_card.uid])
    print(result.__dict__)
    assert result.exit_code == 0
