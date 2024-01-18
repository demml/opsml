# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json as py_json
from pathlib import Path
from typing import Any, Dict, Optional, cast

import httpx
from tenacity import retry, stop_after_attempt

PATH_PREFIX = "opsml"


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
    MODEL_METRICS = "models/metrics"
    DOWNLOAD_FILE = "files/download"
    DELETE_FILE = "files/delete"
    LIST_FILES = "files/list"
    UPLOAD_FILE = "files/upload"
    FILE_EXISTS = "files/exists"


api_routes = ApiRoutes()
_TIMEOUT_CONFIG = httpx.Timeout(10, read=120, write=120)


class ApiClient:
    def __init__(
        self,
        base_url: str,
        username: Optional[str],
        password: Optional[str],
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
        self.client = httpx.Client()

        if token is not None:
            self.client.headers = httpx.Headers({"X-Prod-Token": token})

        if username is not None and password is not None:
            self.client.auth = httpx.BasicAuth(
                username=username,
                password=password,
            )

        self.client.timeout = _TIMEOUT_CONFIG

        self._base_url = self._get_base_url(
            base_url=base_url,
            path_prefix=path_prefix,
        )

    @property
    def base_url(self) -> str:
        """Base url for api client"""
        return self._base_url

    def _get_base_url(self, base_url: str, path_prefix: str) -> str:
        """Gets the base url to use with all requests"""
        return f"{base_url}/{path_prefix}"

    @retry(reraise=True, stop=stop_after_attempt(3))
    def post_request(
        self,
        route: str,
        json: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        response = self.client.post(
            url=f"{self._base_url}/{route}",
            json=json,
        )

        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())

        detail = response.json().get("detail")
        raise ValueError(f"""Failed to to make server call for post request Url: {route}, {detail}""")

    @retry(reraise=True, stop=stop_after_attempt(1))
    def get_request(self, route: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        response = self.client.get(url=f"{self._base_url}/{route}", params=params)

        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())

        detail = response.json().get("detail")
        raise ValueError(f"""Failed to to make server call for get request Url: {route}, {detail}""")

    @retry(reraise=True, stop=stop_after_attempt(3))
    def stream_post_request(
        self, route: str, files: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = ""

        with self.client.stream(
            method="POST", url=f"{self._base_url}/{route}", files=files, headers=headers
        ) as response:
            for data in response.iter_bytes():
                result += data.decode("utf-8")

        response_result = cast(Dict[str, Any], py_json.loads(result))

        if response.status_code == 200:
            return response_result

        raise ValueError(
            f"""
            Failed to to make server call for post request Url: {route}.
            {response_result.get("detail")}
            """
        )

    @retry(reraise=True, stop=stop_after_attempt(3))
    def stream_download_file_request(
        self, route: str, local_dir: Path, filename: str, read_dir: Path
    ) -> Dict[str, Any]:
        local_dir.mkdir(parents=True, exist_ok=True)  # for subdirs that may be in path
        read_path = read_dir / filename
        local_path = local_dir / filename

        with open(local_path.as_posix(), "wb") as local_file:
            with self.client.stream(
                method="GET", url=f"{self._base_url}/{route}", params={"path": read_path.as_posix()}
            ) as response:
                for data in response.iter_bytes():
                    local_file.write(data)

        if response.status_code == 200:
            return {"status": 200}  # filler return

        response_result = cast(
            Dict[str, Any],
            py_json.loads(data.decode("utf-8")),  # pylint: disable=undefined-loop-variable
        )

        raise ValueError(
            f"""Failed to to make server call for post request Url: {ApiRoutes.DOWNLOAD_FILE}.
              {response_result.get("detail")}
            """
        )
