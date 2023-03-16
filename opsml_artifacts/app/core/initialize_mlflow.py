# pylint: disable-all
import sys

import mlflow
from mlflow.utils.server_cli_utils import resolve_default_artifact_root

from opsml_artifacts.app.core.config import MlFlowConfig
from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


def initialize_mlflow() -> MlFlowConfig:
    """Initializes the mlflow server.
    This must be ran before HTTP serving begins. It simulates the cli launching the server.
    Raises:
        ValueError: One or more env vars is missing.
    """
    mlflow_config = MlFlowConfig()
    if mlflow_config.MLFLOW_SERVER_FILE_STORE is None or len(mlflow_config.MLFLOW_SERVER_FILE_STORE) == 0:
        raise ValueError("_MLFLOW_SERVER_FILE_STORE env var is invalid")
    if (
        mlflow_config.MLFLOW_SERVER_ARTIFACT_DESTINATION is None
        or len(mlflow_config.MLFLOW_SERVER_ARTIFACT_DESTINATION) == 0
    ):
        raise ValueError("_MLFLOW_SERVER_ARTIFACT_DESTINATION env var is invalid")
    if mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT is None or len(mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT) == 0:
        raise ValueError("_MLFLOW_SERVER_ARTIFACT_ROOT env var is invalid")

    backend_store_uri = mlflow_config.MLFLOW_SERVER_FILE_STORE
    registry_store_uri = backend_store_uri
    default_artifact_root = mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT

    default_artifact_root = resolve_default_artifact_root(True, default_artifact_root, backend_store_uri)

    try:
        mlflow.server.handlers.initialize_backend_stores(backend_store_uri, registry_store_uri, default_artifact_root)

        return mlflow_config

    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.error("Error initializing backend store")
        logger.exception(error)
        sys.exit(1)
