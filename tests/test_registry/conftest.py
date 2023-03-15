import pytest
import os
from typing import Any
from unittest.mock import patch, MagicMock
from opsml_artifacts.registry.sql.sql_schema import DataSchema, ModelSchema, ExperimentSchema, PipelineSchema
from opsml_artifacts.registry.sql.registry import CardRegistry
from opsml_artifacts.registry.sql.connectors.connector import LocalSQLConnection
from opsml_artifacts.scripts.load_model_card import ModelLoaderCli
from opsml_artifacts.registry.model.types import ModelApiDef


@pytest.fixture(scope="function")
def mock_local_engine():
    local_client = LocalSQLConnection(tracking_uri="sqlite://")
    engine = local_client.get_engine()
    return engine


@pytest.fixture(scope="function")
def db_registries(mock_local_engine):

    tmp_db_path = f"{os.path.expanduser('~')}/tmp.db"
    sql_path = f"sqlite:///{tmp_db_path}"

    os.environ["OPSML_TRACKING_URI"] = sql_path
    os.environ["OPSML_STORAGE_URI"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_ARTIFACT_DESTINATION"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_ARTIFACT_ROOT"] = f"{os.path.expanduser('~')}/mlruns"
    os.environ["_MLFLOW_SERVER_FILE_STORE"] = sql_path
    os.environ["_MLFLOW_SERVER_SERVE_ARTIFACTS"] = "true"

    with patch.multiple(
        "opsml_artifacts.registry.sql.connectors.connector.LocalSQLConnection",
        get_engine=MagicMock(return_value=mock_local_engine),
    ) as engine_mock:

        local_client = LocalSQLConnection(tracking_uri="sqlite://")
        engine = local_client.get_engine()

        DataSchema.__table__.create(bind=engine, checkfirst=True)
        ModelSchema.__table__.create(bind=engine, checkfirst=True)
        ExperimentSchema.__table__.create(bind=engine, checkfirst=True)
        PipelineSchema.__table__.create(bind=engine, checkfirst=True)

        model_registry = CardRegistry(registry_name="model")
        data_registry = CardRegistry(registry_name="data")
        experiment_registry = CardRegistry(registry_name="experiment")
        pipeline_registry = CardRegistry(registry_name="pipeline")

        yield {
            "data": data_registry,
            "model": model_registry,
            "experiment": experiment_registry,
            "pipeline": pipeline_registry,
            "connection_client": local_client,
        }


@pytest.fixture(scope="function")
def mock_model_cli_loader(db_registries):
    model_registry = db_registries["model"]
    from pathlib import Path

    class MockModelLoaderCli(ModelLoaderCli):
        def _write_api_json(self, api_def: ModelApiDef, filepath: Path) -> None:
            pass

        def _set_registry(self) -> Any:
            return model_registry

    with patch("opsml_artifacts.scripts.load_model_card.ModelLoaderCli", MockModelLoaderCli) as mock_cli_loader:

        yield mock_cli_loader
