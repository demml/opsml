from functools import cached_property
from typing import Any, Dict, Optional, Union

from opsml.scouter import DriftType
from opsml.scouter.client import ScouterApiClient
from opsml.scouter.server import SCOUTER_SERVER_CLIENT as scouter_server_client
from opsml.scouter.server import ScouterServerClient
from opsml.settings.config import config
from opsml.storage import client
from opsml.storage.client import ApiStorageClient


def _set_client() -> Optional[Union[ScouterServerClient, ScouterApiClient]]:
    """Helper function to set the client based whether opsml is running in server or client mode"""

    if config.is_tracking_local:
        if scouter_server_client is None:
            return None

        assert isinstance(scouter_server_client, ScouterServerClient)
        return scouter_server_client

    assert isinstance(client.storage_client, ApiStorageClient)
    return ScouterApiClient()


class ScouterClient:
    """Helper class for scouter integration"""

    def __init__(self) -> None:
        """Setup scouter client. Will also check if scouter server is up"""
        self._client = _set_client()
        self._scouter_set = self._client is not None and self.healthcheck()

    @property
    def server_running(self) -> bool:
        """Check if scouter server is running"""
        return self._scouter_set

    @cached_property
    def _scouter_client(self) -> Union[ScouterServerClient, ScouterApiClient]:
        assert self._client is not None
        return self._client

    def healthcheck(self) -> bool:
        """Checks if scouter server is up. Will return False if scouter is not running or the healthcheck fails

        Returns:
            True if server is up, False otherwise
        """
        assert self._client is not None

        try:
            return self._client.healthcheck()

        # silent failure is scouter is not running
        except Exception:  # pylint: disable=broad-except
            return False

    def update_profile_status(self, repository: str, name: str, version: str, active: bool) -> None:
        """Sets the profile to active

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            active:
                Status to set
        """

        self._scouter_client.update_drift_profile_status(
            repository=repository,
            name=name,
            version=version,
            active=active,
        )

    def insert_drift_profile(self, drift_profile: str, drift_type: DriftType) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
            drift_type:
                Drift type
        """

        self._scouter_client.insert_drift_profile(
            drift_profile=drift_profile,
            drift_type=drift_type,
        )

    def update_drift_profile(
        self,
        repository: str,
        name: str,
        version: str,
        drift_profile: str,
        drift_type: DriftType,
        save: bool = False,
    ) -> None:
        """Updates drift profile into scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            save:
                Save flag
            drift_profile:
                Drift profile
            drift_type:
                Drift type
        """

        self._scouter_client.update_drift_profile(
            repository=repository,
            name=name,
            version=version,
            save=save,
            drift_profile=drift_profile,
            drift_type=drift_type,
        )

    def get_drift_profile(self, repository: str, name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get drift profile from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version

        Returns:
            Drift profile
        """
        return self._scouter_client.get_drift_profile(
            repository=repository,
            name=name,
            version=version,
        )
