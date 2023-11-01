# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json as py_json
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast

import httpx
from tenacity import retry, stop_after_attempt

PATH_PREFIX = "opsml"


class ApiRoutes:
    CHECK_UID = "cards/uid"
    VERSION = "cards/version"
    LIST_CARDS = "cards/list"
    SETTINGS = "settings"
    CREATE_CARD = "cards/create"
    UPDATE_CARD = "cards/update"
    DELETE_CARD = "cards/delete"
    DATA_PROFILE = "data/profile"
    COMPARE_DATA = "data/compare"
    UPLOAD = "upload"
    REGISTER_MODEL = "models/register"
    MODEL_METADATA = "models/metadata"
    MODEL_METRICS = "models/metrics"
    COMPARE_MODEL_METRICS = "models/compare_metrics"
    DOWNLOAD_FILE = "files/download"
    DELETE_FILE = "files/delete"
    LIST_FILES = "files/list"


api_routes = ApiRoutes()
TIMEOUT_CONFIG = httpx.Timeout(10, read=120, write=120)
OPSML_PROD_TOKEN = os.environ.get("OPSML_PROD_TOKEN", "staging")
default_headers = httpx.Headers({"X-Prod-Token": OPSML_PROD_TOKEN})


class ApiClient:
    def __init__(
        self,
        base_url: str,
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
        self.client.timeout = TIMEOUT_CONFIG
        self.client.headers = default_headers

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
            return response.json()

        detail = response.json().get("detail")
        raise ValueError(f"""Failed to to make server call for post request Url: {route}, {detail}""")

    @retry(reraise=True, stop=stop_after_attempt(3))
    def get_request(self, route: str) -> Dict[str, Any]:
        response = self.client.get(url=f"{self._base_url}/{route}")

        if response.status_code == 200:
            return response.json()

        raise ValueError(f"""Failed to to make server call for get request Url: {route}""")

    @retry(reraise=True, stop=stop_after_attempt(3))
    def stream_post_request(
        self,
        route: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        result = ""
        with self.client.stream(
            method="POST",
            url=f"{self._base_url}/{route}",
            files=files,
            headers=headers,
            json=json,
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
        self,
        route: str,
        local_dir: str,
        filename: str,
        read_dir: str,
    ) -> Dict[str, Any]:
        Path(local_dir).mkdir(parents=True, exist_ok=True)  # for subdirs that may be in path

        read_path = os.path.join(read_dir, filename)
        with open(os.path.join(local_dir, filename), "wb") as local_file:
            with self.client.stream(
                method="POST",
                url=f"{self._base_url}/{route}",
                json={"read_path": read_path},
            ) as response:
                for data in response.iter_bytes():
                    local_file.write(data)

        if response.status_code == 200:
            return {"status": 200}  # filler return

        response_result = cast(
            Dict[str, Any], py_json.loads(data.decode("utf-8"))  # pylint: disable=undefined-loop-variable
        )

        raise ValueError(
            f"""Failed to to make server call for post request Url: {ApiRoutes.DOWNLOAD_FILE}.
              {response_result.get("detail")}
            """
        )
