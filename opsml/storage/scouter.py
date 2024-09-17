import json

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
        self.request(route="/profile", request_type=RequestType.POST, json=profile)


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
