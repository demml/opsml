import os
from functools import cached_property
from typing import Any, Dict, Optional, cast

import httpx
from pydantic import BaseSettings, Field, root_validator

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.models import (
    GcsStorageClientSettings,
    StorageClientSettings,
    StorageSettings,
)
from opsml_artifacts.helpers.request_helpers import ApiClient, api_routes
from opsml_artifacts.registry.cards.storage_system import (
    StorageClientGetter,
    StorageClientTypes,
)
from opsml_artifacts.registry.sql.connectors import BaseSQLConnection, SQLConnector

BASE_LOCAL_SQL = f"sqlite:///{os.path.expanduser('~')}/opsml_artifacts_database.db"
OPSML_STORAGE_URI = "OPSML_STORAGE_URI"
OPSML_TRACKING_URI = "OPSML_TRACKING_URI"
OPSML_USERNAME = "OPSML_USERNAME"
OPSML_PASSWORD = "OPSML_PASSWORD"

logger = ArtifactLogger.get_logger(__name__)


class StorageSettingsGetter:
    def __init__(self, storage_uri: Optional[str] = None):
        self.storage_uri = storage_uri

    def _get_gcs_info(self) -> GcsStorageClientSettings:
        storage_settings: Dict[str, Any] = {}
        from opsml_artifacts.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
            GcpCredsSetter,
        )

        gcp_creds = GcpCredsSetter().get_creds()
        storage_settings["credentials"] = gcp_creds.creds
        storage_settings["storage_type"] = "gcs"
        storage_settings["storage_uri"] = self.storage_uri
        storage_settings["gcp_project"] = gcp_creds.project

        return GcsStorageClientSettings(**storage_settings)

    def _get_default_info(self) -> StorageClientSettings:
        return StorageClientSettings(storage_uri=self.storage_uri)

    def get_storage_settings(self) -> StorageSettings:
        if self.storage_uri is not None:
            if "gs://" in self.storage_uri:
                return self._get_gcs_info()
            return self._get_default_info()
        return StorageClientSettings()


class DefaultAttrCreator:
    def __init__(self, env_vars: Dict[str, Any]):
        """Class for setting default attributes for DefaulSettings

        Args:
            env_vars (dict): Dictionary of key value pairs
        """
        self._env_vars = env_vars
        self.tracking_uri = self._set_tracking_uri()

        self._set_storage_client()

    def _set_tracking_uri(self) -> str:
        """Sets tracking url to use for database entries

        Returns:
            tracking_uri string

        """
        tracking_uri = self._env_vars.get(OPSML_TRACKING_URI.lower(), BASE_LOCAL_SQL)

        if tracking_uri is BASE_LOCAL_SQL:
            logger.info("""No tracking url set. Defaulting to Sqlite""")

        self._env_vars[OPSML_TRACKING_URI.lower()] = tracking_uri
        self._get_api_client(tracking_uri=tracking_uri)

        return tracking_uri

    def _set_storage_client(self) -> None:
        """Sets storage info and storage client attributes for DefaultSettings"""

        self._get_storage_settings()
        self._env_vars["storage_client"] = StorageClientGetter.get_storage_client(
            storage_settings=self._env_vars["storage_settings"],
        )

    def _get_api_client(self, tracking_uri: str) -> None:
        """Checks if tracking url is an http and sets a request client

        Args:
            tracking_uri (str): URL for tracking
        """

        username = os.environ.get(OPSML_USERNAME)
        password = os.environ.get(OPSML_PASSWORD)

        if "http" in tracking_uri:
            request_client = ApiClient(base_url=tracking_uri)
            if all(bool(cred) for cred in [username, password]):
                request_client.client.auth = httpx.BasicAuth(
                    username=str(username),
                    password=str(password),
                )
            self._env_vars["request_client"] = request_client

    def _get_storage_settings(self) -> None:
        """Sets storage info based on tracking url. If tracking url is
        http then external api will be used to get storage info. If no
        external api is detected, local defaults will be used.

        Args:
            opsml_tracking_uri (str): Tracking url for opsml database entries

        Returns:
            StorageClientSettings pydantic Model
        """

        if self._env_vars.get("request_client") is not None:
            self._env_vars["storage_settings"] = self._get_storage_settings_from_api()

        else:
            self._env_vars["storage_settings"] = self._get_storage_settings_from_local()

    def _get_storage_settings_from_api(self) -> StorageSettings:
        """Gets storage info from external opsml api

        Args:
            opsml_tracking_uri (str): External opsml api

        Returns:
            StorageClientSettings

        """
        request_client = cast(ApiClient, self._env_vars.get("request_client"))
        storage_settings = request_client.get_request(route=api_routes.SETTINGS)

        return StorageSettingsGetter(
            storage_uri=storage_settings.get("storage_uri"),
        ).get_storage_settings()

    def _get_storage_settings_from_local(self) -> StorageSettings:
        """Gets storage info from external opsml api

        Returns:
            StorageClientSettings

        """
        storage_uri = os.environ.get(OPSML_STORAGE_URI)
        return StorageSettingsGetter(
            storage_uri=storage_uri,
        ).get_storage_settings()

    @property
    def env_vars(self):
        """Return dictionary are key value pairings for DefaultSettings"""
        return self._env_vars


class DefaultConnector:
    def __init__(
        self,
        tracking_uri: str,
        credentials: Optional[Any],
    ):
        self.tracking_uri = tracking_uri
        self.credentials = credentials

    def _get_connector_type(self) -> str:
        """Gets the sql connection type when running opsml locally (without api proxy)"""

        connector_type = "local"
        for db_type in ["postgresql", "mysql"]:
            if db_type in self.tracking_uri:
                connector_type = db_type

        if "cloudsql" in self.tracking_uri:
            connector_type = f"cloudsql_{connector_type}"

        return connector_type

    def _get_sql_connector(self, connector_type: str):
        """Gets the sql connection given a connector type"""
        return SQLConnector.get_connector(connector_type=connector_type)

    def get_connector(self) -> BaseSQLConnection:
        """Gets the sql connector to use when running opsml locally (without api proxy)"""
        connector_type = self._get_connector_type()
        connector = self._get_sql_connector(connector_type=connector_type)

        return connector(
            tracking_uri=self.tracking_uri,
            credentials=self.credentials,
        )


class DefaultSettings(BaseSettings):
    """Default variables to load"""

    app_env: str = Field("development", env="APP_ENV")
    opsml_tracking_uri: str = Field(..., env=OPSML_TRACKING_URI)
    storage_settings: StorageSettings
    storage_client: StorageClientTypes
    request_client: Optional[ApiClient] = Field(None)

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)
        validate_assignment = True

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

        if hasattr(self.storage_settings, "credentials"):
            credentials = self.storage_settings.credentials
        else:
            credentials = None

        return DefaultConnector(
            tracking_uri=self.opsml_tracking_uri,
            credentials=credentials,
        ).get_connector()

    def set_storage(self, storage_settings: StorageSettings) -> None:
        """Set storage url and storage client from storage_uri

        Args:
            storage_uri (str): Optional storage url
        """

        storage_client = StorageClientGetter.get_storage_client(storage_settings=storage_settings)

        setattr(self, "storage_settings", storage_settings)
        setattr(self, "storage_client", storage_client)


settings = DefaultSettings()
