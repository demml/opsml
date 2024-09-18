import json
from typing import Any, Dict, Optional, cast

from opsml.settings.config import config
from opsml.storage.api import ApiClient, RequestType


class ScouterClient(ApiClient):
    def insert_drift_profile(self, drift_profile: str) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
        """
        profile = json.loads(drift_profile)
        self.request(route="profile", request_type=RequestType.POST, json=profile)

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
        response = self.request(
            route="profile",
            request_type=RequestType.GET,
            params={
                "repository": repository,
                "name": name,
                "version": version,
            },
        )

        if response["status"] == "error":
            return None

        return cast(Dict[str, Any], response["profile"])

    def get_drift_values(
        self,
        repository: str,
        name: str,
        version: str,
        time_window: str,
        max_data_points: int,
        feature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get drift values from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            time_window:
                Time window
            max_data_points:
                Maximum data points

        Returns:
            Drift values
        """
        params = {
            "repository": repository,
            "name": name,
            "version": version,
            "time_window": time_window,
            "max_data_points": max_data_points,
        }

        if feature:
            params["feature"] = feature

        response = self.request(route="drift", request_type=RequestType.GET, params=params)

        return cast(Dict[str, Any], response["data"])


SCOUTER_CLIENT = None
if config.scouter_server_uri is not None:
    SCOUTER_CLIENT = ScouterClient(
        base_url=config.scouter_server_uri,
        username=config.scouter_username,
        password=config.scouter_password,
        use_auth=config.scouter_auth,
        token=None,
        path_prefix=config.scouter_path_prefix,
    )
