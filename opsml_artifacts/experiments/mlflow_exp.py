import os
from typing import Optional
import mlflow
from mlflow.entities import RunStatus, Run
from mlflow.tracking import MlflowClient
from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.sql.registry import CardTypes
from opsml_artifacts.experiments.mlflow_helpers import log_card_artifacts, MlFLowCardRegistries

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
        self.experiment_name = experiment_name.lower()

        # set the registries
        self.registries = MlFLowCardRegistries(
            datacard=CardRegistry(registry_name="data"),
            modelcard=CardRegistry(registry_name="model"),
            experimentcard=CardRegistry(registry_name="experiment"),
        )
        self.active_run: Optional[Run] = None

    def _set_experiment(self) -> str:
        """Sets the experiment to use with mlflow. If an experiment id associated
        with an experiment name does not exist it is created

        Returns:
            exp_id
        """
        exp_id = self.get_experiment_by_name(self.experiment_name)
        if exp_id is None:
            exp_id = self.create_experiment(name=self.experiment_name)

        return exp_id

    def _set_run(self, exp_id: str) -> Run:

        """Sets the run id for the experiment. If an existing run_id is passed,
        The tracking client activates the run. If no existing run_id is passed,
        A new run is created.

        Args:
            exp_id (str): Experiment id

        Returns:
            MlFlow Run
        """

        existing_run_id = os.environ.get("OPSML_RUN_ID")
        if bool(existing_run_id):
            self._tracking_client.update_run(
                run_id=existing_run_id,
                status=RunStatus.RUNNING,
            )
            return self._tracking_client.get_run(existing_run_id)

        return self._tracking_client.create_run(experiment_id=exp_id)

    def __enter__(self):

        exp_id = self._set_experiment()
        self.active_run = self._set_run(exp_id=exp_id)
        logger.info("starting experiment")

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._tracking_client.set_terminated(run_id=self.active_run.info.run_id)
        logger.info("experiment complete")

    def register_card(self, artifact_card: CardTypes, version_type: str = "minor"):
        """Register a given artifact card

        Args:
            artifact_card (CardTypes): DataCard or ModelCard
            version_type (str): Version type for increment. Options are "major", "minor" and
            "patch". Defaults to "minor"
        """

        card_type = artifact_card.__class__.__name__.lower()
        registry: CardRegistry = getattr(self.registries, card_type)
        registry.register_card(card=artifact_card, version_type=version_type)

        logger.info("Logging artifact")
        card_logger = log_card_artifacts(
            card_type=card_type,
            artifact_card=artifact_card,
            run_id=self.active_run.info.run_id,
            client=self._tracking_client,
        )
        card_logger.u
