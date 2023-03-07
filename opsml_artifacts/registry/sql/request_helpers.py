import requests
from typing import Optional, Dict, Any


def post_request(session: requests.Session, url: str, json: Optional[Dict[str, Any]]) -> Any:

    response = session.post(url=url, json=json)
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve data from api. {response.json()}")

    return response.json()


def get_request(session: requests.Session, url: str) -> Any:

    response = session.get(url=url)
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve data from api. {response.json()}")

    return response.json()
