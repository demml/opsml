import base64
import json
import os
from datetime import datetime
from typing import List, Tuple, Union

import google.auth
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pydantic import BaseModel, Extra
from pyshipt_logging import ShiptLogging

from opsml_artifacts.helpers.models import SnowflakeParams
from opsml_artifacts.helpers.utils import GCPClient

logger = ShiptLogging.get_logger(__name__)


# specific for shipt
class OpsmlCreds:
    def __init__(self):
        self.user_creds = None
        self.project_name = None
        self.service_base_creds = None
        self.secret_client = None
        self.service_base64_creds = os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")

    def set_gcp_sdk_creds(self) -> None:
        """Pulls google cloud sdk creds from local env

        Returns
            Tuple containing user credentials and project name
        """
        self.user_creds, _ = google.auth.default()
        self.project_name = self.user_creds.quota_project_id

    @property
    def has_service_base64_creds(self) -> bool:
        """Has environment creds"""
        return bool(self.service_base64_creds)

    def create_secret_client(self):
        self.secret_client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=self.user_creds,
        )

    def decode_base64(self) -> str:
        base_64 = base64.b64decode(s=self.service_base64_creds).decode("utf-8")
        return json.loads(base_64)

    def create_gcp_creds_from_base64(self) -> Tuple[Credentials, str]:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name
        """
        key = self.decode_base64()
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key)  # noqa
        project_name = service_creds.project_id

        return service_creds, project_name

    def get_opsml_creds(
        self,
        service_account_secret_name: str,
    ) -> Tuple[Credentials, str]:

        if not self.has_service_base64_creds:
            self.set_gcp_sdk_creds()
            self.create_secret_client()
            self.service_base64_creds = self.secret_client.get_secret(
                project_name=self.project_name,
                secret_name=service_account_secret_name,
            )

        service_creds, project_name = self.create_gcp_creds_from_base64()

        return service_creds, project_name


# to be used with Settings class
class GCPEnvSetter:
    def __init__(self):
        self.attributes = {}
        self.attributes["app_env"] = os.environ.get("APP_ENV", "staging")
        self.env_vars = [
            "gcp_region",
            "gcs_bucket",
            "snowflake_api_auth",
            "snowflake_api_url",
            "db_name",
            "db_instance_name",
            "db_username",
            "db_password",
        ]

        self.secret_names = [
            "gcp_pipeline_region",
            "gcs_pipeline_bucket",
            "snowflake_api_auth",
            "snowflake_api_url",
            "artifact_registry_db_name",
            "artifact_registry_instance_name",
            "artifact_registry_username",
            "artifact_registry_password",
        ]

        self.set_gcp_env_secrets()

    def set_gcp_credentials(self):
        """Sets gcp credentials"""

        secret_name = f"opsml_service_creds_{self.attributes['app_env']}"
        gcp_creds, gcp_project = OpsmlCreds().get_opsml_creds(service_account_secret_name=secret_name)
        service_account_email = getattr(gcp_creds, "service_account_email", None)

        key_names = ["gcp_creds", "gcp_project", "service_account"]
        values = [gcp_creds, gcp_project, service_account_email]

        self._append_to_attributes(key_names=key_names, values=values)

    def _append_to_attributes(
        self,
        key_names: List[str],
        values: List[Union[str, int]],
    ):
        for key, value in zip(key_names, values):
            self.attributes[key] = value

    def set_env_variables_from_secrets(self, env_vars: List[str], secret_names: List[str]):

        """Loads gcp project secrets

        Args:
            attributes (Dict): Dictionary of key value pairs of attributes
            env_vars (List): List of environment variable names
            secret_names (List): List of secret names in gcp


        Returns
            Dictionary of attributes
        """

        secret_client = GCPClient.get_service(
            service_name="secret_manager", gcp_credentials=self.attributes["gcp_creds"]
        )

        secret_values = []
        for secret_name in secret_names:
            secret_values.append(
                secret_client.get_secret(project_name=self.attributes["gcp_project"], secret=secret_name)
            )

        self._append_to_attributes(key_names=env_vars, values=secret_values)

    def set_gcp_env_secrets(self):
        self.set_gcp_credentials()
        self.set_env_variables_from_secrets(env_vars=self.env_vars, secret_names=self.secret_names)

        # remove this once networking is figured out
        scopes = "https://www.googleapis.com/auth/devstorage.full_control"
        self.attributes["gcsfs_creds"] = self.attributes["gcp_creds"].with_scopes([scopes])


class Settings(BaseModel):
    """Creates base settings used through package"""

    gcp_project: str
    gcs_bucket: str
    gcp_region: str
    run_id: str = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    app_env: str
    path: str = os.getcwd()
    gcp_creds: Credentials
    snowflake_api_auth: str
    snowflake_api_url: str
    db_username: str
    db_password: str
    db_name: str
    db_instance_name: str
    gcsfs_creds = str

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True


env_setter = GCPEnvSetter()
settings = Settings(**env_setter.attributes)


class SnowflakeCredentials:
    @staticmethod
    def credentials() -> SnowflakeParams:
        login_vars = {}
        secret_client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=settings.gcp_creds,
        )
        for secret in SnowflakeParams.__annotations__.keys():  # pylint: disable=no-member
            value = secret_client.get_secret(
                project_name=settings.gcp_project,
                secret=f"snowflake_{secret}",
            )

            login_vars[secret] = value

        return SnowflakeParams(**login_vars)
