# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json as py_json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, cast

import httpx
from tenacity import retry, stop_after_attempt

from opsml.settings.config import config

# httpx outputs a lot of logs
logging.getLogger("httpx").propagate = False

PATH_PREFIX = "opsml"


# do not need to be unique
class RequestType(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    STREAM_POST = "POST"
    STREAM_GET = "GET"


class ApiRoutes:
    CHECK_UID = "cards/uid"
    VERSION = "cards/version"
    LIST_CARDS = "cards/list"
    REPOSITORY_CARDS = "cards/repositories"
    NAME_CARDS = "cards/names"
    TABLE_NAME = "registry/table"
    CREATE_CARD = "cards/create"
    UPDATE_CARD = "cards/update"
    DELETE_CARD = "cards/delete"
    DATA_PROFILE = "data/profile"
    COMPARE_DATA = "data/compare"
    REGISTER_MODEL = "models/register"
    MODEL_METADATA = "models/metadata"
    PROJECT_ID = "projects/id"
    METRICS = "metrics"
    DOWNLOAD_FILE = "files/download"
    DELETE_FILE = "files/delete"
    LIST_FILES = "files/list"
    UPLOAD_FILE = "files/upload"
    FILE_EXISTS = "files/exists"
    TOKEN = "auth/token"
    HW_METRICS = "metrics/hardware"


api_routes = ApiRoutes()
_TIMEOUT_CONFIG = httpx.Timeout(10, read=120, write=120)


class ApiClient:
    def __init__(
        self,
        base_url: str,
        username: Optional[str],
        password: Optional[str],
        use_auth: bool,
        token: Optional[str],
        path_prefix: str = PATH_PREFIX,
    ):
        """Instantiates Api client for interacting with opsml server

        Args:
            base_url:
                Base url of server
            path_prefix:
                Prefix for opsml server path

        """
        self._requires_auth = False
        self._auth_token = None
        self.client = httpx.Client()
        self._base_url = self._get_base_url(base_url=base_url, path_prefix=path_prefix)

        if token is not None:
            self.client.headers = httpx.Headers({"X-Prod-Token": token})
            self.client.headers["X-Prod-Token"] = token

        if use_auth:
            assert (
                username is not None and password is not None
            ), "Username and password must be provided when using authentication"
            self._requires_auth = True
            self.form_data = {"username": config.opsml_username, "password": config.opsml_password}
            self.refresh_token()

        self.client.timeout = _TIMEOUT_CONFIG

    def _get_base_url(self, base_url: str, path_prefix: str) -> str:
        """Gets the base url to use with all requests"""
        return f"{base_url}/{path_prefix}"

    def refresh_token(self) -> None:
        """Refreshes the token"""

        if self._requires_auth:
            response = self.client.post(url=f"{self._base_url}/{ApiRoutes.TOKEN}", data=self.form_data)
            res = response.json()

            # check if token is in response
            if "access_token" not in res:
                raise ValueError(f"Failed to get access token: {res.get('detail')}")

            self._auth_token = res["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self._auth_token}"

    @retry(reraise=True, stop=stop_after_attempt(3))
    def request(self, route: str, request_type: RequestType, **kwargs: Any) -> Dict[str, Any]:
        """Makes a request to the server

        Args:
            route:
                Route to make request to
            request_type:
                Type of request to make
            **kwargs:
                Keyword arguments for request

        Returns:
            Response from server
        """
        try:
            url = f"{self._base_url}/{route}"
            response = getattr(self.client, request_type.value.lower())(url=url, **kwargs)

            if response.status_code == 200:
                return cast(Dict[str, Any], response.json())

            detail = response.json().get("detail")
            self.refresh_token()

            raise ValueError(f"""Failed to make server call for {request_type} request Url: {route}, {detail}""")

        except Exception as exc:
            raise exc

    @retry(reraise=True, stop=stop_after_attempt(3))
    def stream_post_request(
        self,
        route: str,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        result = ""

        # self.refresh_token()
        url = f"{self._base_url}/{route}"
        with self.client.stream(method="POST", url=url, files=files, headers=headers) as response:
            for data in response.iter_bytes(chunk_size=chunk_size):
                result += data.decode("utf-8")

        response_result = cast(Dict[str, Any], py_json.loads(result))

        if response.status_code == 200:
            return response_result

        self.refresh_token()
        raise ValueError(
            f"""
            Failed to make server call for post request Url: {route}.
            {response_result.get("detail")}
            """
        )

    @retry(reraise=True, stop=stop_after_attempt(3))
    def stream_download_file_request(
        self, route: str, local_dir: Path, filename: str, read_dir: Path, chunk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        local_dir.mkdir(parents=True, exist_ok=True)  # for subdirs that may be in path
        read_path = read_dir / filename
        local_path = local_dir / filename
        url = f"{self._base_url}/{route}"

        with open(local_path.as_posix(), "wb") as local_file:
            with self.client.stream(method="GET", url=url, params={"path": read_path.as_posix()}) as response:
                for data in response.iter_bytes(chunk_size=chunk_size):
                    local_file.write(data)

        if response.status_code == 200:
            return {"status": 200}  # filler return

        response_result = cast(
            Dict[str, Any],
            py_json.loads(data.decode("utf-8")),  # pylint: disable=undefined-loop-variable
        )

        self.refresh_token()
        raise ValueError(
            f"""Failed to make server call for post request Url: {ApiRoutes.DOWNLOAD_FILE}.
              {response_result.get("detail")}
            """
        )
