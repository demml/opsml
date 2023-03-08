import functools
from typing import Any, Dict, Optional

import requests

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


def retry(api_call):
    @functools.wraps(api_call)
    def wrapper_decorator(*args, **kwargs) -> Dict[str, Any]:
        retries = 0
        while retries < 5:
            response: requests.Response = api_call(*args, **kwargs)
            if response.status_code == 200:
                return response.json()
            retries += 1
        raise ValueError(f"Failed to retrieve data from api. {response.json()}")

    return wrapper_decorator


@retry
def post_request(session: requests.Session, url: str, json: Optional[Dict[str, Any]]) -> Any:

    response = session.post(url=url, json=json)
    return response


@retry
def get_request(session: requests.Session, url: str) -> Any:

    response = session.get(url=url)

    return response
