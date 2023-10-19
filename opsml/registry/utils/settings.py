# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from functools import cached_property
from typing import Any, Dict, Optional, cast

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
import sqlalchemy
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiClient, api_routes
from opsml.helpers.types import OpsmlAuth, OpsmlUri
from opsml.registry.sql.connectors import BaseSQLConnection, SQLConnector
from opsml.registry.storage.storage_system import (
    StorageClientGetter,
    StorageClientType,
    StorageSystem,
)
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientSettings,
    StorageSettings,
)

BASE_LOCAL_SQL = f"sqlite:///{os.path.expanduser('~')}/opsml_database.db"
STORAGE_URI = f"{os.path.expanduser('~')}/opsml_artifacts"


logger = ArtifactLogger.get_logger()


class StorageSettingsGetter:
    def __init__(
        self,
        storage_uri: Optional[str] = None,
        storage_type: str = StorageSystem.LOCAL.value,
    ):
        self.storage_uri = storage_uri
        self.storage_type = storage_type

    def _get_gcs_settings(self) -> GcsStorageClientSettings:
        from opsml.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
            GcpCredsSetter,
        )

        gcp_creds = GcpCredsSetter().get_creds()

        return GcsStorageClientSettings(
            storage_type=self.storage_type,
            storage_uri=self.storage_uri,
            gcp_project=gcp_creds.project,
            credentials=gcp_creds.creds,
        )

    def _get_api_storage_settings(self) -> ApiStorageClientSettings:
        """Returns storage settings for using Api storage class"""
        return ApiStorageClientSettings(
            storage_type=self.storage_type,
            storage_uri=self.storage_uri,
        )

    def _get_s3_settings(self) -> S3StorageClientSettings:
        return S3StorageClientSettings(
            storage_type=self.storage_type,
            storage_uri=self.storage_uri,
        )

    def _get_default_settings(self) -> StorageClientSettings:
        return StorageClientSettings(
            storage_uri=self.storage_uri,
            storage_type=self.storage_type,
        )

    def get_storage_settings(self) -> StorageSettings:
        if self.storage_type == StorageSystem.GCS:
            return self._get_gcs_settings()

        if self.storage_type == StorageSystem.API:
            return self._get_api_storage_settings()

        if self.storage_type == StorageSystem.S3:
            return self._get_s3_settings()

        if self.storage_uri is not None:
            return self._get_default_settings()

        return StorageClientSettings()


class DefaultAttrCreator:
    def __init__(self, env_vars: Dict[str, Any]):
        """Class for setting default attributes for Settings

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

        tracking_uri = self._env_vars.get(OpsmlUri.TRACKING_URI.lower(), BASE_LOCAL_SQL)

        if tracking_uri is BASE_LOCAL_SQL:
            logger.info("""No tracking url set. Defaulting to Sqlite""")

        self._env_vars[OpsmlUri.TRACKING_URI.lower()] = tracking_uri
        self._get_api_client(tracking_uri=tracking_uri)

        return tracking_uri

    def _set_storage_client(self) -> None:
        """Sets storage info and storage client attributes for DefaultSettings"""

        storage_settings = self._get_storage_settings()

        if isinstance(storage_settings, ApiStorageClientSettings):
            storage_settings.client = self._env_vars["request_client"]

        self._env_vars["storage_client"] = StorageClientGetter.get_storage_client(
            storage_settings=storage_settings,
        )

        self._env_vars["storage_settings"] = storage_settings

    def _get_api_client(self, tracking_uri: str) -> None:
        """Checks if tracking url is http and sets a request client

        Args:
            tracking_uri (str): URL for tracking
        """

        username = os.environ.get(OpsmlAuth.USERNAME)
        password = os.environ.get(OpsmlAuth.PASSWORD)

        if "http" in tracking_uri:
            request_client = ApiClient(base_url=tracking_uri.strip("/"))
            if all(bool(cred) for cred in [username, password]):
                request_client.client.auth = httpx.BasicAuth(
                    username=str(username),
                    password=str(password),
                )
            self._env_vars["request_client"] = request_client

    def _get_storage_settings(self) -> StorageSettings:
        """Sets storage info based on tracking url. If tracking url is
        http then external api will be used to get storage info. If no
        external api is detected, local defaults will be used.

        Args:
            opsml_tracking_uri (str): Tracking url for opsml database entries

        Returns:
            StorageClientSettings pydantic Model
        """

        if self._env_vars.get("request_client") is not None:
            return self._get_storage_settings_from_api()

        return self._get_storage_settings_from_local()

    def _get_storage_settings_from_api(self) -> StorageSettings:
        """
        Gets storage info from external opsml api

        Args:
            opsml_tracking_uri:
                External opsml api

        Returns:
            StorageClientSettings

        """
        request_client = cast(ApiClient, self._env_vars.get("request_client"))
        storage_settings = request_client.get_request(route=api_routes.SETTINGS)

        storage_uri = storage_settings.get("storage_uri")
        storage_type = storage_settings.get("storage_type")

        return StorageSettingsGetter(
            storage_uri=storage_uri,
            storage_type=str(storage_type),
        ).get_storage_settings()

    def _get_storage_type(self, storage_uri: str) -> str:
        if "gs://" in storage_uri:
            return StorageSystem.GCS.value
        if "s3://" in storage_uri:
            return StorageSystem.S3.value
        return StorageSystem.LOCAL.value

    def _get_storage_settings_from_local(self) -> StorageSettings:
        """
        Gets storage info from external opsml api

        Returns:
            StorageClientSettings

        """
        storage_uri = os.environ.get(OpsmlUri.STORAGE_URI, STORAGE_URI)

        if storage_uri is not None:
            storage_type = self._get_storage_type(storage_uri=storage_uri)
            return StorageSettingsGetter(
                storage_uri=storage_uri,
                storage_type=storage_type,
            ).get_storage_settings()

        raise ValueError("Missing OPSML_STORAGE_URI env variable")

    @property
    def env_vars(self):
        """Return dictionary are key value pairings for DefaultSettings"""
        return self._env_vars


class DefaultConnector:
    def __init__(
        self,
        tracking_uri: str,
        credentials: Optional[Any] = None,
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

    model_config = SettingsConfigDict(
        frozen=False,
        arbitrary_types_allowed=True,
        ignored_types=(cached_property,),
        validate_assignment=True,
    )

    app_env: str = "development"
    opsml_tracking_uri: str
    storage_settings: StorageSettings
    storage_client: StorageClientType
    request_client: Optional[ApiClient] = None

    @model_validator(mode="before")
    def set_base_settings(cls, env_vars) -> Dict[str, Any]:
        """Sets tracking url if it doesn't exist and sets storage
        client-related vars
        """
        return DefaultAttrCreator(env_vars=env_vars).env_vars

    @cached_property
    def connection_client(self) -> BaseSQLConnection:
        """Retrieve sql connection client.
        Connection client is only used in the Registry class.
        """
        return DefaultConnector(
            tracking_uri=self.opsml_tracking_uri,
            credentials=None,
        ).get_connector()

    @cached_property
    def sql_engine(self) -> sqlalchemy.engine.base.Engine:
        """Retrieve sql engine"""

        return self.connection_client.sql_engine

    def set_storage(self, storage_settings: StorageSettings) -> None:
        """
        Set storage url and storage client from storage_uri

        Args:
            storage_settings:
                StorageClientSettings pydantic Model
        """

        storage_client = StorageClientGetter.get_storage_client(storage_settings=storage_settings)

        setattr(self, "storage_settings", storage_settings)
        setattr(self, "storage_client", storage_client)


settings = DefaultSettings()
