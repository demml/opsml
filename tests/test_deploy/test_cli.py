from click.testing import CliRunner
from opsml.deploy.fastapi.api import deploy_uvicorn, deploy_gunicorn
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient


def test_uvicorn(fastapi_model_app):
    with patch.multiple(
        "opsml.deploy.fastapi.api.ModelApi",
        run=MagicMock(return_value=TestClient(fastapi_model_app)),
    ) as test_client:

        runner = CliRunner()
        result = runner.invoke(deploy_uvicorn, ["--port", 8000])
        assert result.exit_code == 0


def test_gunicorn(fastapi_model_app):
    with patch.multiple(
        "opsml.deploy.fastapi.gunicorn.GunicornApplication",
        run=MagicMock(return_value=TestClient(fastapi_model_app)),
    ) as test_client:
        runner = CliRunner()
        result = runner.invoke(deploy_gunicorn, ["--port", 8000])
        assert result.exit_code == 0
