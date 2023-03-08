import os
from functools import cached_property
from typing import Any, Dict, Optional, Tuple

import requests
from pydantic import BaseSettings, Field, root_validator

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.models import (
    GcsStorageClientInfo,
    StorageClientInfo,
    StorageInfo,
)
from opsml_artifacts.helpers.request_helpers import get_request
from opsml_artifacts.registry.cards.storage_system import (
    StorageClientGetter,
    StorageClientTypes,
)
from opsml_artifacts.registry.sql.connectors import BaseSQLConnection, SQLConnector

OPSML_PREFIX = "opsml"
STORAGE_CLIENT_PATH = "storage_client"


logger = ArtifactLogger.get_logger(__name__)


class DefaultSettings(BaseSettings):
    """Default variables to load"""

    app_env: str = Field("development", env="APP_ENV")
    opsml_tacking_url: str = Field(..., env="OPSML_TRACKING_URL")
    storage_info: StorageInfo
    storage_client: StorageClientTypes
    request_client: Optional[requests.Session] = Field(None)

    class Config:
        allow_mutation = True
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @root_validator(pre=True)
    def set_base_settings(cls, env_vars) -> Dict[str, Any]:  # pylint: disable=no-self-argument

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
        tracking_url = env_vars.get("opsml_tacking_url")

        if tracking_url is not None:
            return env_vars, tracking_url

        logger.info("""No tracking url set. Defaulting to Sqlite""")

        tracking_url = "sqlite://"
        env_vars["opsml_tacking_url"] = tracking_url
        return env_vars, tracking_url

    @classmethod
    def _get_api_client(
        cls,
        env_vars: Dict[str, Any],
        tracking_url: str,
    ) -> Dict[str, Any]:

        username = os.environ.get("OPSML_USERNAME")
        password = os.environ.get("OPSML_USERNAME")

        if "http" in tracking_url:
            request_client = requests.Session()
            if all(bool(cred) for cred in [username, password]):
                request_client.auth = (str(username), str(password))
            env_vars["request_client"] = request_client
        return env_vars

    @staticmethod
    def _get_storage_info(env_vars: Dict[str, Any], tracking_url: str) -> StorageInfo:
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
            return DefaultSettings._get_storage_info_from_api(request_client, tracking_url)
        return DefaultSettings._get_storage_info_from_local()

    @staticmethod
    def _get_storage_info_from_api(
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

            from opsml_artifacts.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
                GcpCredsSetter,
            )

            gcp_creds = GcpCredsSetter().get_creds()
            storage_info["credentials"] = gcp_creds.creds
            storage_info["gcp_project"] = gcp_creds.project

            return GcsStorageClientInfo(**storage_info)

        return StorageClientInfo(**storage_info)

    @staticmethod
    def _get_storage_info_from_local(storage_url: Optional[str] = None) -> StorageClientInfo:
        """Gets storage info from external opsml api

        Returns:
            StorageClientInfo

        """
        storage_info: Dict[str, Any] = {}
        storage_url = os.environ.get("OPSML_STORAGE_URL", storage_url)

        if storage_url is not None:
            if "gs://" in storage_url:
                from opsml_artifacts.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
                    GcpCredsSetter,
                )

                gcp_creds = GcpCredsSetter().get_creds()
                storage_info["credentials"] = gcp_creds.creds
                storage_info["storage_type"] = "gcs"
                storage_info["storage_url"] = storage_url
                storage_info["gcp_project"] = gcp_creds.project

                return GcsStorageClientInfo(**storage_info)

        else:
            logger.info(
                """No storage specified for local client. Default to local host""",
            )

        return StorageClientInfo(**storage_info)

    @cached_property
    def connection_client(self) -> BaseSQLConnection:
        """Retrieve sql connection client"""

        connector_type = "local"
        for db_type in ["postgresql", "mysql"]:
            if db_type in self.opsml_tacking_url:
                connector_type = db_type

        if "cloudsql" in self.opsml_tacking_url:
            connector_type = f"cloudsql_{connector_type}"

        connector = SQLConnector.get_connector(connector_type=connector_type)

        if hasattr(self.storage_info, "credentials"):
            credentials = self.storage_info.credentials
        else:
            credentials = None

        return connector(
            tracking_url=self.opsml_tacking_url,
            credentials=credentials,
        )

    def set_storage_url(self, storage_url: str) -> None:
        """Set storage url and storage client from storage_url

        Args:
            storage_url (str): Optional storage url
        """

        storage_info = self._get_storage_info_from_local(storage_url=storage_url)
        storage_client = StorageClientGetter.get_storage_client(storage_info=storage_info)

        setattr(self, "storage_info", storage_info)
        setattr(self, "storage_client", storage_client)


settings = DefaultSettings()
