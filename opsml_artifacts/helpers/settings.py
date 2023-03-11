import os
from functools import cached_property
from typing import Any, Dict, Optional, Tuple
import httpx
from pydantic import BaseSettings, Field, root_validator

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.models import (
    GcsStorageClientInfo,
    StorageClientInfo,
    StorageInfo,
)
from opsml_artifacts.helpers.request_helpers import ApiClient
from opsml_artifacts.helpers.models import ApiRoutes
from opsml_artifacts.registry.cards.storage_system import (
    StorageClientGetter,
    StorageClientTypes,
)
from opsml_artifacts.registry.sql.connectors import BaseSQLConnection, SQLConnector


BASE_LOCAL_SQL = f"sqlite:///{os.path.expanduser('~')}/opsml_artifacts_database.db"

logger = ArtifactLogger.get_logger(__name__)


class StorageInfoGetter:
    def __init__(self, storage_url: Optional[str] = None):
        self.storage_url = storage_url

    def _get_gcs_info(self) -> GcsStorageClientInfo:
        storage_info: Dict[str, Any] = {}
        from opsml_artifacts.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
            GcpCredsSetter,
        )

        gcp_creds = GcpCredsSetter().get_creds()
        storage_info["credentials"] = gcp_creds.creds
        storage_info["storage_type"] = "gcs"
        storage_info["storage_url"] = self.storage_url
        storage_info["gcp_project"] = gcp_creds.project

        return GcsStorageClientInfo(**storage_info)

    def _get_default_info(self) -> StorageClientInfo:
        return StorageClientInfo(storage_url=self.storage_url)

    def get_storage_info(self) -> StorageInfo:
        if self.storage_url is not None:
            if "gs://" in self.storage_url:
                return self._get_gcs_info()
            return self._get_default_info()
        return StorageClientInfo()


class DefaultAttrCreator:
    def __init__(self, env_vars: Dict[str, Any]):
        """Class for setting default attributes for DefaulSettings

        Args:
            env_vars (dict): Dictionary of key value pairs
        """
        self._env_vars = env_vars
        self.tracking_url = self._set_tracking_url()

        self._set_storage_client()

    def _set_tracking_url(self) -> Tuple[Dict[str, Any], str]:
        """Sets tracking url to use for database entries

        Returns:
            tracking_url string

        """
        tracking_url = self._env_vars.get("opsml_tacking_url")

        if tracking_url is not None:
            self._get_api_client(tracking_url=tracking_url)
            return tracking_url

        logger.info("""No tracking url set. Defaulting to Sqlite""")
        self._env_vars["opsml_tacking_url"] = BASE_LOCAL_SQL
        return tracking_url

    def _set_storage_client(self) -> None:
        """Sets storage info and storage client attributes for DefaultSettings"""

        self._get_storage_info()
        self._env_vars["storage_client"] = StorageClientGetter.get_storage_client(
            storage_info=self._env_vars["storage_info"],
        )

    def _get_api_client(self, tracking_url: str) -> None:
        """Checks if tracking url is an http and sets a request client

        Args:
            tracking_url (str): URL for tracking
        """

        username = os.environ.get("OPSML_USERNAME")
        password = os.environ.get("OPSML_PASSWORD")

        if "http" in tracking_url:
            request_client = ApiClient()
            if all(bool(cred) for cred in [username, password]):
                request_client.client.auth = httpx.BasicAuth(
                    username=str(username),
                    password=str(password),
                )
            self._env_vars["request_client"] = request_client

    def _get_storage_info(self) -> StorageInfo:
        """Sets storage info based on tracking url. If tracking url is
        http then external api will be used to get storage info. If no
        external api is detected, local defaults will be used.

        Args:
            opsml_tracking_url (str): Tracking url for opsml database entries

        Returns:
            StorageClientInfo pydantic Model
        """

        if self._env_vars.get("request_client") is not None:
            self._env_vars["storage_info"] = self._get_storage_info_from_api()

        else:
            self._env_vars["storage_info"] = self._get_storage_info_from_local()

    def _get_storage_info_from_api(self) -> StorageInfo:
        """Gets storage info from external opsml api

        Args:
            opsml_tracking_url (str): External opsml api

        Returns:
            StorageClientInfo

        """
        request_client = self._env_vars.get("request_client")
        storage_info = request_client.get_request(
            url=f"{self.tracking_url}/{ApiRoutes.STORAGE_PATH.value}",
        )

        return StorageInfoGetter(storage_url=storage_info.get("storage_url")).get_storage_info()

    def _get_storage_info_from_local(self) -> StorageInfo:
        """Gets storage info from external opsml api

        Returns:
            StorageClientInfo

        """
        storage_url = os.environ.get("OPSML_STORAGE_URL")
        return StorageInfoGetter(storage_url=storage_url).get_storage_info()

    @property
    def env_vars(self):
        """Return dictionary are key value pairings for DefaultSettings"""
        return self._env_vars


class DefaultConnector:
    def __init__(
        self,
        tracking_url: str,
        credentials: Optional[Any],
    ):
        self.tracking_url = tracking_url
        self.credentials = credentials

    def _get_connector_type(self) -> str:

        connector_type = "local"
        for db_type in ["postgresql", "mysql"]:
            if db_type in self.tracking_url:
                connector_type = db_type

        if "cloudsql" in self.tracking_url:
            connector_type = f"cloudsql_{connector_type}"

        return connector_type

    def _get_sql_connector(self, connector_type: str):
        return SQLConnector.get_connector(connector_type=connector_type)

    def get_connector(self) -> BaseSQLConnection:
        connector_type = self._get_connector_type()
        connector = self._get_sql_connector(connector_type=connector_type)

        return connector(
            tracking_url=self.tracking_url,
            credentials=self.credentials,
        )


class DefaultSettings(BaseSettings):
    """Default variables to load"""

    app_env: str = Field("development", env="APP_ENV")
    opsml_tacking_url: str = Field(..., env="OPSML_TRACKING_URL")
    storage_info: StorageInfo
    storage_client: StorageClientTypes
    request_client: Optional[ApiClient] = Field(None)

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @root_validator(pre=True)
    def set_base_settings(cls, env_vars) -> Dict[str, Any]:  # pylint: disable=no-self-argument
        """Sets tracking url if it doesnt exist and sets storage
        client-related vars
        """

        return DefaultAttrCreator(env_vars=env_vars).env_vars

    @cached_property
    def connection_client(self) -> BaseSQLConnection:
        """Retrieve sql connection client.
        Connection client is only used in the Registry class.
        """

        if hasattr(self.storage_info, "credentials"):
            credentials = self.storage_info.credentials
        else:
            credentials = None

        return DefaultConnector(
            tracking_url=self.opsml_tacking_url,
            credentials=credentials,
        ).get_connector()

    def set_storage(self, storage_info: StorageInfo) -> None:
        """Set storage url and storage client from storage_url

        Args:
            storage_url (str): Optional storage url
        """

        storage_client = StorageClientGetter.get_storage_client(storage_info=storage_info)

        setattr(self, "storage_info", storage_info)
        setattr(self, "storage_client", storage_client)


settings = DefaultSettings()
