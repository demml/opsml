from typing import Dict, Tuple
from typer.testing import CliRunner
from sklearn import linear_model
import pandas as pd
from opsml.scripts.api_cli import app
from opsml.registry import DataCard, ModelCard, CardRegistries
import tempfile
from starlette.testclient import TestClient

runner = CliRunner()


def test_download_model(
    api_registries: CardRegistries,
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
    assert result.exit_code == 0


def _test_launch_server(test_app, api_registries, linear_regression):
    result = runner.invoke(app, ["launch-server"])
    assert result.exit_code == 0
