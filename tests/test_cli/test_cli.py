from typer.testing import CliRunner
from opsml.scripts.download_model import app
from opsml.registry import DataCard, ModelCard

runner = CliRunner()


def test_app(test_app, api_registries, linear_regression):
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

    result = runner.invoke(app, ["--name", "test_model", "--team", team])
    assert result.exit_code == 0
