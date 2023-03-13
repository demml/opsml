import os
from typing import Optional
import mlflow
from mlflow.tracking import MlflowClient
from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.sql.registry import CardTypes
from opsml_artifacts.experiments.mlflow_helpers import ModelCardLogger

# Notes during development
# assume you are using mlflow url with a proxy client for artifacts
#  Add ApiRegistry with call paths to update opsml
# Needs: Absolute path for mlflow artifacts (base bucket path)

logger = ArtifactLogger.get_logger(__name__)
SKLEARN_FLAVOR = ["sklearn"]


class MlFlowExperiment(MlflowClient):
    def __init__(
        self,
        experiment_name: str,
        team_name: str,
        user_email: str,
        tracking_uri: Optional[str] = None,
        registry_uri: Optional[str] = None,
    ):

        super().__init__(
            tracking_uri=tracking_uri,
            registry_uri=registry_uri,
        )
        self.team_name = team_name
        self.user_email = user_email
        self.run_id = os.getenv("OPSML_RUN_ID")
        self.experiment_name = experiment_name.lower()

        # set storage
        self._set_storage()

        # set the registries
        self.registries = {
            "datacard": {"registry": CardRegistry(registry_name="data")},
            "modelcard": {
                "registry": CardRegistry(registry_name="model"),
                "logger": ModelCardLogger,
            },
            "experimentcard": CardRegistry(registry_name="experiment"),
        }

    def __enter__(self):

        exp_id = self.get_experiment_by_name(self.experiment_name)
        if exp_id is None:
            self.create_experiment(name=self.experiment_name)

        run = mlflow.start_run(
            run_id=self.run_id,
            experiment_id=self.experiment_id,
        )

        self.run_id = run.info.run_id
        self.artifact_uri = run.info.artifact_uri
        logger.info("starting experiment")

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        mlflow.end_run()
        logger.info("experiment complete")

    def register_card(self, artifact_card: CardTypes, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            artifact_card (CardTypes): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        trackers = self.registries[artifact_card.__name__.lower()]
        registry: CardRegistry = trackers.get("registry")
        logger = trackers.get("logger")
        registry.register_card(artifact_card, version_type=version_type)

        if artifact_card.__name__.lower() == "modelcard":
            card_logger = logger(
                card=artifact_card,
                client=self._tracking_client,
                run_id=self.run_id,
            )
            card_logger.log_model_artifacts()

        logger.info("Logging artifact")
