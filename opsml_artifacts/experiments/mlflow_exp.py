from opsml_artifacts import CardRegistry
from opsml_artifacts.registry.sql.registry import CardTypes
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.helpers.logging import ArtifactLogger

from mlflow.tracking import MlflowClient
import os

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
# TODO: Add ApiRegistry with call paths to update opsml
# Needs: Absolute path for mlflow artifacts (base bucket path)

logger = ArtifactLogger.get_logger(__name__)


class MlFlowExperiment(MlflowClient):
    def __init__(self, experiment_name: str, tracking_uri: str):

        super().__init__(tracking_uri=tracking_uri)
        self._set_storage_url()

        self.run_id = os.getenv("OPSML_RUN_ID")
        self.experiment_name = experiment_name.lower()

        # set the registries
        self.registries = {
            "datacard": CardRegistry(registry_name="data"),
            "modelcard": CardRegistry(registry_name="model"),
            "experimentcard": CardRegistry(registry_name="exp"),
        }

    def _set_storage_url(self):
        """Set the storage url for OpsML. Mlflow artifact proxy requires
        writing to local prior to uploading to mlflow server. If using proxy,
        Opsml needs to be configured to store artifacts locally.
        """
        store = self._tracking_client.store.__class__.__name__.lower()
        if store == "reststore":
            # httpproxy requires saving files to local
            # need to set opsml storage client to local
            settings.set_storage_url(storage_url="local")

    def register(self, artifact_card: CardTypes, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            artifact_card (CardTypes): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        registry: CardRegistry = self.registries[artifact_card.__name__.lower()]
        registry.register_card(artifact_card, version_type=version_type)

        logger.info("Logging artifact")
