from typer.testing import CliRunner
from opsml.scripts.api_cli import app

runner = CliRunner()


def test_download_model_fail():
    team = "mlops"

    result = runner.invoke(app, ["--name", "test_model", "--team", team])
    assert result.exit_code == 1
