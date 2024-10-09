from typing import Any, Dict, Optional, cast

from opsml.scouter import DriftType
from opsml.storage import client
from opsml.storage.api import RequestType, api_routes
from opsml.storage.client import ApiStorageClient


class ScouterApiClient:
    def __init__(self) -> None:
        assert isinstance(client.storage_client, ApiStorageClient)
        self._client = client.storage_client.api_client

    def healthcheck(self) -> bool:
        """Checks if scouter server is up

        Returns:
            True if server is up, False otherwise
        """
        response = self._client.request(route=api_routes.SCOUTER_HEALTHCHECK, request_type=RequestType.GET)

        return bool(response.get("running"))

    def insert_drift_profile(self, drift_profile: str, drift_type: DriftType) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
            drift_type:
                Drift type
        """
        self._client.request(
            route=api_routes.SCOUTER_DRIFT_PROFILE,
            request_type=RequestType.POST,
            json={
                "profile": drift_profile,
                "drift_type": drift_type.value,
            },
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
        self._client.request(
            route=api_routes.SCOUTER_DRIFT_PROFILE,
            request_type=RequestType.PUT,
            json={
                "repository": repository,
                "name": name,
                "version": version,
                "profile": drift_profile,
                "drift_type": drift_type.value,
                "save": save,
            },
        )

    def update_drift_profile_status(self, repository: str, name: str, version: str, active: bool) -> Dict[str, str]:
        """Updates drift profile status into scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            status:
                Status to update
        """

        return self._client.request(
            route=api_routes.SCOUTER_DRIFT_PROFILE_STATUS,
            request_type=RequestType.PUT,
            json={
                "name": name,
                "repository": repository,
                "version": version,
                "active": active,
            },
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
        response = self._client.request(
            route=api_routes.SCOUTER_DRIFT_PROFILE,
            request_type=RequestType.GET,
            params={
                "repository": repository,
                "name": name,
                "version": version,
            },
        )

        if response["status"] == "error":
            return None

        return cast(Dict[str, Any], response["data"])
