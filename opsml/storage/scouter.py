import json

from opsml.settings.config import config
from opsml.storage.api import ApiClient, RequestType
from scouter import DriftProfile


class ScouterClient(ApiClient):
    def insert_drift_profile(self, drift_profile: str) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
        """
        profile = json.loads(drift_profile)
        self.request(route="profile", request_type=RequestType.POST, json=profile)

    def get_drift_profile(self, repository: str, name: str, version: str) -> DriftProfile:
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

        return DriftProfile(**response["data"])


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
