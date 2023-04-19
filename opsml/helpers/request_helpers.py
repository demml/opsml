from typing import Any, Dict, Optional
import os
import httpx
from tenacity import retry, stop_after_attempt
import json as py_json

PATH_PREFIX = "opsml"


class ApiRoutes:
    CHECK_UID = "check_uid"
    VERSION = "version"
    LIST = "list"
    SETTINGS = "settings"
    CREATE = "create"
    UPDATE = "update"
    UPLOAD = "upload"
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

        with self.client.stream(
            method="POST",
            url=f"{self._base_url}/{route}",
            files=files,
            headers=headers,
            json=json,
        ) as response:

            for data in response.iter_bytes():
                result = data.decode("utf-8")

        result = py_json.loads(result)
        if response.status_code == 200:
            return result

        raise ValueError(
            f"""Failed to to make server call for post request Url: {ApiRoutes.UPLOAD}, {result.get("detail")}"""
        )

    # need to write another method for downloading files
    @retry(stop=stop_after_attempt(3))
    def stream_download_file_request(
        self,
        route: str,
        local_path: str,
        read_path: str,
        filename: str,
    ) -> Dict[str, Any]:

        with open(os.path.join(local_path, filename), "wb") as local_file:
            with self.client.stream(
                method="POST",
                url=f"{self._base_url}/{route}",
                json={"read_path": os.path.join(read_path, filename)},
            ) as response:

                for data in response.iter_bytes():
                    local_file.write(data)

        if response.status_code == 200:
            return None

        result = py_json.loads(data.decode("utf-8"))

        raise ValueError(
            f"""Failed to to make server call for post request Url: {ApiRoutes.DOWNLOAD_FILE}, {result.get("detail")}"""
        )

    # @retry(stop=stop_after_attempt(3))
    # def download_file(self, local_path: str, read_path: str) -> Dict[str, Any]:


#
#    with self.client.stream(
#        method="POST",
#        url=f"{self._base_url}/{ApiRoutes.DOWNLOAD_FILE}",
#        json=json
#    ):
#        pass
#
#    raise ValueError(
#        f"""Failed to to make server call for post request Url: {ApiRoutes.UPLOAD}, {response.reason_phrase}"""
#    )
