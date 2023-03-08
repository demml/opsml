import functools
from typing import Any, Dict, Optional

import requests


def retry(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        retries = 0
        while retries < 5:
            try:
                value = func(*args, **kwargs)
                return value
            except Exception as error:
                retries += 1
        raise error

    return wrapper_decorator


@retry
def post_request(session: requests.Session, url: str, json: Optional[Dict[str, Any]]) -> Any:

    response = session.post(url=url, json=json)
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve data from api. {response.json()}")

    return response.json()


@retry
def get_request(session: requests.Session, url: str) -> Any:

    response = session.get(url=url)
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve data from api. {response.json()}")

    return response.json()
