import base64
import json
import os
from typing import Any, Dict, Optional, Tuple, cast

import google.auth
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pydantic import root_validator
from pyshipt_logging import ShiptLogging

from opsml_artifacts.helpers.gcp_utils import GCPClient, GCPSecretManager
from opsml_artifacts.helpers.models import (
    GcpCreds,
    GcpVariables,
    Settings,
    SnowflakeParams,
)

logger = ShiptLogging.get_logger(__name__)


class GcpCredsSetter:
    def __init__(self):
        """Set credentials"""

        self.service_base64_creds: Optional[str] = os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")  # type: ignore

    def get_creds(self) -> GcpCreds:
        service_base64_creds = self.get_base64_creds()
        service_creds, project_name = self.create_gcp_creds_from_base64(service_base64_creds=service_base64_creds)

        return GcpCreds(
            creds=service_creds,
            project=project_name,
        )

    def get_base64_creds(self) -> str:
        if not self.has_service_base64_creds:
            return self.get_service_creds_from_user_info("ml_service_creds")
        return cast(str, self.service_base64_creds)

    @property
    def has_service_base64_creds(self) -> bool:
        """Has environment creds"""
        return bool(self.service_base64_creds)

    def get_gcp_sdk_creds(self) -> Tuple[Credentials, str]:
        """Pulls google cloud sdk creds from local env

        Returns
            Tuple containing user credentials and project name
        """
        user_creds, _ = google.auth.default()
        project_name = user_creds.quota_project_id

        return user_creds, project_name

    def create_secret_client(self, user_creds: Credentials) -> GCPSecretManager:
        secret_client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=user_creds,
        )
        return cast(GCPSecretManager, secret_client)

    def decode_base64(self, service_base64_creds: str) -> str:
        base_64 = base64.b64decode(s=service_base64_creds).decode("utf-8")
        return json.loads(base_64)

    def create_gcp_creds_from_base64(self, service_base64_creds: str) -> Tuple[Credentials, str]:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name
        """
        key = self.decode_base64(service_base64_creds=service_base64_creds)
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key)  # noqa
        project_name = service_creds.project_id

        return service_creds, project_name

    def get_service_creds_from_user_info(self, service_account_secret_name: str) -> str:
        user_creds, project_name = self.get_gcp_sdk_creds()
        secret_client = self.create_secret_client(user_creds=user_creds)
        service_base64_creds: str = secret_client.get_secret(
            project_name=project_name,
            secret=service_account_secret_name,
        )

        return service_base64_creds


class GcpSecretVarGetter:
    def __init__(self, gcp_credentials: GcpCreds):
        self.gcp_creds = gcp_credentials
        client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=self.gcp_creds.creds,
        )
        self.secret_client = cast(GCPSecretManager, client)

    def get_secret(self, secret_name: str) -> str:
        return self.secret_client.get_secret(
            project_name=self.gcp_creds.project,
            secret=secret_name,
        )


class GlobalSettings(Settings):
    @root_validator(pre=True)
    def get_env_vars(cls, env_vars):  # pylint: disable=no-self-argument)
        creds = GcpCredsSetter().get_creds()
        env_vars["gcp_creds"] = creds.creds
        env_vars["path"] = os.getcwd()

        # replace gcsfs with gcs
        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        env_vars["gcsfs_creds"] = creds.creds.with_scopes([scopes])
        env_vars = cls.load_vars_from_gcp(env_vars=env_vars, gcp_credentials=creds)

        return env_vars

    @classmethod
    def load_vars_from_gcp(cls, env_vars: Dict[str, Any], gcp_credentials: GcpCreds):
        secret_getter = GcpSecretVarGetter(gcp_credentials=gcp_credentials)
        logger.info("Loading environment variables")

        for name, value in {i.name.lower(): i.value for i in GcpVariables}.items():
            env_vars[name] = secret_getter.get_secret(secret_name=value)

        return env_vars


class MockSettings(Settings):
    class Config:
        arbitrary_types_allowed = True


def get_settings():
    if bool(os.getenv("ARTIFACT_TESTING_MODE")):
        from opsml_artifacts.helpers.fixtures.mock_vars import mock_vars  # pylint: disable=import-outside-toplevel

        return MockSettings(**mock_vars)
    return GlobalSettings()


settings = get_settings()


class SnowflakeCredentials:
    @staticmethod
    def credentials() -> SnowflakeParams:
        login_vars = {}
        secret_client = cast(
            GCPSecretManager,
            GCPClient.get_service(
                service_name="secret_manager",
                gcp_credentials=settings.gcp_creds,
            ),
        )
        for secret in SnowflakeParams.__annotations__.keys():  # pylint: disable=no-member
            value = secret_client.get_secret(
                project_name=settings.gcp_project,
                secret=f"snowflake_{secret}",
            )

            login_vars[secret] = value

        return SnowflakeParams(**login_vars)
