# pylint: disable=invalid-envvar-value
from typing import Optional, Any, Iterator, cast
from dataclasses import dataclass
from contextlib import contextmanager

from opsml_artifacts import VersionType, CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.projects.types import CardRegistries

from opsml_artifacts.registry.cards import ArtifactCard
from opsml_artifacts.registry.cards.types import CardInfo, CardType
from opsml_artifacts.registry.storage.storage_system import StorageClient

logger = ArtifactLogger.get_logger(__name__)


class Project:
    """
    A project is a top level container for storing artifacts.

    Each project contains one or more runs. A run is typically an instance of a
    model training run. Artifacts (cards) are associated with a run.
    """

    @property
    def run_id(self) -> str:
        """Current run id associated with project"""
        if self._run_mgr.run_id is not None:
            return self._run_mgr.run_id
        raise ValueError("Run id not set for current project")

    @run_id.setter
    def run_id(self, run_id: str):
        """Set the run_id to use with the active project"""
        self._run_mgr.run_id = run_id

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def run_data(self) -> Any:
        return self._run_mgr.mlflow_client.get_run(self.run_id).data

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> Iterator[ActiveRun]:
        """
        Starts mlflow run for project

        Args:
            run_name:
                Optional run name
        """

        self._run_mgr.start_run(run_name=run_name)

        yield cast(ActiveRun, self._run_mgr.active_run)

        self._run_mgr.end_run()

    def load_card(self, card_type: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            card_type:
                datacard or modelcard
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.

        Returns
            `ArtifactCard`
        """
        card_type = CardType(card_type.lower()).name.lower()
        return CardHandler.load_card(
            registries=self._run_mgr.registries,
            card_type=card_type,
            info=info,
        )

    def download_artifacts(
        self,
        artifact_path: Optional[str] = None,
        local_path: Optional[str] = None,
    ) -> str:
        """
        Download an artifact or artifacts associated with a run_id

        Args:
            artifact_path:
                Optional path that contains artifact(s) to download
            local_path:
                Local path (directory) to download artifacts to

        Returns:
            Artifact path
        """
        raise NotImplementedError

    def list_artifacts(self) -> dict[str, float]:
        """List artifacts for the current run"""
        return self._run_mgr.mlflow_client.list_artifacts(
            run_id=self.run_id,
        )

    @property
    def metrics(self) -> dict[str, float]:
        return self.run_data.metrics

    @property
    def params(self) -> dict[str, str]:
        return self.run_data.params

    @property
    def tags(self) -> dict[str, str]:
        return self.run_data.tags
