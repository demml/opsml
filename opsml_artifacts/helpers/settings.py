from typing import Any, Dict, Optional, Union, Tuple
import requests
from requests.adapters import HTTPAdapter, Retry
from pydantic import BaseSettings, Field, root_validator, BaseModel
import os
from opsml_artifacts.helpers.logging import ArtifactLogger

# Set retries for calling api
retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("http://", HTTPAdapter(max_retries=retries))

OPSML_PREFIX = "opsml"
STORAGE_CLIENT_PATH = "storage_client"

logger = ArtifactLogger.get_logger(__name__)


class StorageClientInfo(BaseModel):
    credentials: Optional[Any] = None
    storage_type: str = "local"
    storage_url: str = os.path.expanduser("~")


class OpsmlSettings(BaseSettings):
    """Default variables to load"""

    app_env: str = Field("development", env="APP_ENV")
    opsml_tacking_url: str = Field(..., env="OPSML_TRACKING_URL")
    storage_info: StorageClientInfo

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def set_base_settings(cls, env_vars) -> Dict[str, Any]:
        env_vars, tracking_url = cls._set_tracking_url(env_vars=env_vars)
        env_vars["storage_info"] = cls._get_storage_info(opsml_tracking_url=tracking_url)

        return env_vars

    @classmethod
    def _set_tracking_url(
        cls, env_vars: Dict[str, Union[str, StorageClientInfo]]
    ) -> Tuple[Dict[str, Union[str, StorageClientInfo]], str]:
        """Sets tracking url to use for database entries

        Args:
            env_vars (dict): Dictionary of key value pairs

        Returns:
            env_vars dictionary and tracking_url string

        """
        tracking_url = env_vars.get("OPSML_TRACKING_URL")

        if tracking_url is not None:
            return env_vars, tracking_url

        logger.info("""No tracking url set. Defaulting to Sqlite""")

        tracking_url = "sqlite://"
        env_vars["OPSML_TRACKING_URL"] = tracking_url
        return env_vars, tracking_url

    @classmethod
    def _get_storage_info(cls, opsml_tracking_url: str) -> StorageClientInfo:
        """Sets storage info based on tracking url. If tracking url is
        http then external api will be used to get storage info. If no
        external api is detected, local defaults will be used.

        Args:
            opsml_tracking_url (str): Tracking url for opsml database entries

        Returns:
            StorageClientInfo pydantic Model
        """

        if cls._is_http_connection(opsml_tracking_url=opsml_tracking_url):
            return cls._get_storage_info_from_api(opsml_tracking_url)
        return cls._get_storage_info_from_local()

    @classmethod
    def _get_storage_info_from_api(cls, opsml_tracking_url: str) -> StorageClientInfo:
        """Gets storage info from external opsml api

        Args:
            opsml_tracking_url (str): External opsml api

        Returns:
            StorageClientInfo

        """
        response = session.get(f"{opsml_tracking_url}/{OPSML_PREFIX}/{STORAGE_CLIENT_PATH}")
        if response.status_code != 200:
            raise ValueError(f"Error connecting to opsml api. {response.json()}")

        storage_info = response.json()

        if "gcs" in storage_info.get("storage_type"):
            from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter

            storage_info["credentials"] = GcpCredsSetter().get_creds()
        return StorageClientInfo(**storage_info)

    @classmethod
    def _get_storage_info_from_local(cls) -> StorageClientInfo:
        """Gets storage info from external opsml api

        Returns:
            StorageClientInfo

        """
        storage_info: Dict[str, Any]
        storage_url = os.environ.get("OPSML_STORAGE_URL")
        if bool(storage_url):
            if "gcs" in storage_url:
                from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter

                storage_info["credentials"] = GcpCredsSetter().get_creds()
                storage_info["storage_type"] = "gcs"
            storage_info["storage_url"] = storage_url
        else:
            logger.info(
                """No storage specified for local client. Default to local host""",
            )

        return StorageClientInfo(**storage_info)

    @classmethod
    def _is_http_connection(cls, opsml_tracking_url: str) -> bool:

        USERNAME = os.environ.get("OPSML_USERNAME")
        PASSWORD = os.environ.get("OPSML_USERNAME")
        if "https" in opsml_tracking_url:
            if all(bool(cred) for cred in [USERNAME, PASSWORD]):
                session.auth = (USERNAME, PASSWORD)
                return True
            else:
                return True
        return False
