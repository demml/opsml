from typer.testing import CliRunner
from opsml.cli.api_cli import app
import tempfile

runner = CliRunner()


def test_download_model_fail(
    mock_cli_property,
):
    team = "mlops"

    with tempfile.TemporaryDirectory() as tmpdirname:
        result = runner.invoke(
            app, ["download-model", "--name", "test_model", "--team", team, "--write-dir", tmpdirname]
        )
        assert result.exit_code == 1
