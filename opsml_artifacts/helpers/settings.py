from typing import Any, Dict, Tuple, Optional, Type
from functools import cached_property
import requests
from requests.adapters import HTTPAdapter, Retry
from pydantic import BaseSettings, Field, root_validator
import os
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.models import GcsStorageClientInfo, StorageClientInfo, StorageInfo
from opsml_artifacts.registry.cards.storage_system import StorageClientGetter, StorageClientTypes
from opsml_artifacts.registry.sql.request_helpers import get_request
from opsml_artifacts.registry.sql.connectors import SQLConnector, BaseSQLConnection

OPSML_PREFIX = "opsml"
STORAGE_CLIENT_PATH = "storage_client"


logger = ArtifactLogger.get_logger(__name__)


class RequestClient:
    @property
    def client(self):
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        request_session = requests.Session()
        request_session.mount("http://", HTTPAdapter(max_retries=retries))

        return request_session


class OpsmlSettings(BaseSettings):
    """Default variables to load"""

    app_env: str = Field("development", env="APP_ENV")
    opsml_tacking_url: str = Field(..., env="OPSML_TRACKING_URL")
    storage_info: StorageInfo
    storage_client: StorageClientTypes
    request_client: Optional[requests.Session] = Field(None)

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def set_base_settings(cls, env_vars) -> Dict[str, Any]:
        env_vars, tracking_url = cls._set_tracking_url(env_vars=env_vars)
        env_vars = cls._get_api_client(env_vars=env_vars, tracking_url=tracking_url)
        storage_info = cls._get_storage_info(env_vars=env_vars, tracking_url=tracking_url)
        env_vars["storage_info"] = storage_info

        # set storage client
        env_vars["storage_client"] = StorageClientGetter.get_storage_client(storage_info=storage_info)

        return env_vars

    @classmethod
    def _set_tracking_url(cls, env_vars: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
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
    def _get_api_client(
        cls,
        env_vars: Dict[str, Any],
        tracking_url: str,
    ) -> Dict[str, Any]:

        USERNAME = os.environ.get("OPSML_USERNAME")
        PASSWORD = os.environ.get("OPSML_USERNAME")

        if "http" in tracking_url:
            request_client = RequestClient().client
            if all(bool(cred) for cred in [USERNAME, PASSWORD]):
                request_client.auth = (USERNAME, PASSWORD)
            env_vars["request_client"] = request_client
        return env_vars

    @classmethod
    def _get_storage_info(cls, env_vars: Dict[str, Any], tracking_url: str) -> StorageInfo:
        """Sets storage info based on tracking url. If tracking url is
        http then external api will be used to get storage info. If no
        external api is detected, local defaults will be used.

        Args:
            opsml_tracking_url (str): Tracking url for opsml database entries

        Returns:
            StorageClientInfo pydantic Model
        """
        request_client = env_vars.get("request_client")
        if request_client is not None:
            return cls._get_storage_info_from_api(request_client, tracking_url)
        return cls._get_storage_info_from_local()

    @classmethod
    def _get_storage_info_from_api(
        cls,
        request_client: requests.Session,
        tracking_url: str,
    ) -> StorageInfo:
        """Gets storage info from external opsml api

        Args:
            opsml_tracking_url (str): External opsml api

        Returns:
            StorageClientInfo

        """
        storage_info = get_request(
            session=request_client,
            url=f"{tracking_url}/{OPSML_PREFIX}/{STORAGE_CLIENT_PATH}",
        )

        if "gcs" in storage_info.get("storage_type"):
            from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter

            gcp_creds = GcpCredsSetter().get_creds().creds
            storage_info["credentials"] = gcp_creds
            storage_info["gcp_project"] = gcp_creds.quota_project_id

            return GcsStorageClientInfo(*storage_info)

        return StorageClientInfo(**storage_info)

    @classmethod
    def _get_storage_info_from_local(cls) -> StorageClientInfo:
        """Gets storage info from external opsml api

        Returns:
            StorageClientInfo

        """
        storage_info: Dict[str, Any] = {}
        storage_url = os.environ.get("OPSML_STORAGE_URL")
        if storage_url is not None:
            if "gcs" in storage_url:
                from opsml_artifacts.helpers.gcp_utils import GcpCredsSetter

                gcp_creds = GcpCredsSetter().get_creds().creds
                storage_info["credentials"] = gcp_creds
                storage_info["storage_type"] = "gcs"
                storage_info["storage_url"] = storage_url
                storage_info["gcp_project"] = gcp_creds.quota_project_id

                return GcsStorageClientInfo(**storage_info)

        else:
            logger.info(
                """No storage specified for local client. Default to local host""",
            )

        return StorageClientInfo(**storage_info)

    @cached_property
    def connection_client(self) -> Type[BaseSQLConnection]:
        """Retrieve sql connection client"""

        connector_type = "local"
        for db_type in ["postgresql", "mysql"]:
            if db_type in self.opsml_tacking_url:
                connector_type = db_type

        if "cloudsql" in self.opsml_tacking_url:
            connector_type = f"cloudsql_{connector_type}"

        connector = SQLConnector.get_connector(connector_type=connector_type)
        return connector(tracking_url=self.opsml_tacking_url)


settings = OpsmlSettings()
