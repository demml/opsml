import json as py_json
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast

import httpx
from tenacity import retry, stop_after_attempt

PATH_PREFIX = "opsml"


class ApiRoutes:
    CHECK_UID = "check_uid"
    VERSION = "version"
    LIST_CARDS = "list_cards"
    SETTINGS = "settings"
    CREATE_CARD = "create_card"
    UPDATE_CARD = "update_card"
    UPLOAD = "upload"
    DOWNLOAD_MODEL_METADATA = "download_model_metadata"
    DOWNLOAD_FILE = "download_file"
    LIST_FILES = "list_files"


api_routes = ApiRoutes()


class ApiClient:
    def __init__(
        self,
        base_url: str,
        path_prefix: str = PATH_PREFIX,
    ):
        self.client = httpx.Client()

        self._base_url = self._get_base_url(
            base_url=base_url,
            path_prefix=path_prefix,
        )

    def _get_base_url(self, base_url: str, path_prefix: str) -> str:
        """Gets the base url to use with all requests"""
        return f"{base_url}/{path_prefix}"

    @retry(stop=stop_after_attempt(3))
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

    @retry(stop=stop_after_attempt(3))
    def get_request(self, route: str) -> Dict[str, Any]:
        response = self.client.get(url=f"{self._base_url}/{route}")

        if response.status_code == 200:
            return response.json()

        raise ValueError(f"""Failed to to make server call for get request Url: {route}""")

    @retry(stop=stop_after_attempt(3))
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

    @retry(stop=stop_after_attempt(3))
    def stream_download_file_request(
        self,
        route: str,
        local_dir: str,
        filename: str,
        read_dir: Optional[str] = None,
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
