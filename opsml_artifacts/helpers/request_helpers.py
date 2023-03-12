from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class ApiClient:
    def __init__(self):
        self.client = httpx.Client()

    @retry(stop=stop_after_attempt(3))
    def post_request(self, url: str, json: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        response = self.client.post(url=url, json=json)
        if response.status_code == 200:
            return response.json()

        raise ValueError(f"""Failed to to make server call for post request Url: {url}""")

    @retry(stop=stop_after_attempt(3))
    def get_request(self, url: str) -> Dict[str, Any]:

        response = self.client.get(url=url)
        if response.status_code == 200:
            return response.json()

        raise ValueError(f"""Failed to to make server call for get request Url: {url}""")
