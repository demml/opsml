# pylint: disable=invalid-name
import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, ClassVar, List, Tuple

import google.auth
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pyshipt_logging import ShiptLogging

from opsml_data.helpers.models import Params, SnowflakeParams
from opsml_data.helpers.utils import FindPath, GCPClient

logger = ShiptLogging.get_logger(__name__)


# specific for shipt
class OpsmlCreds:
    @staticmethod
    def get_secret_from_gcp(
        user_creds: str,
        service_account_secret_name: str,
        project_name: str,
    ):
        secret_manager = secretmanager.SecretManagerServiceClient(
            credentials=user_creds,
        )
        response = secret_manager.access_secret_version(
            request={"name": f"projects/{project_name}/secrets/{service_account_secret_name}/versions/latest"}  # noqa
        )
        return response.payload.data.decode("UTF-8")

    @staticmethod
    def set_opsml_creds(
        service_account_secret_name: str,
    ) -> Tuple[Credentials, str]:

        if bool(os.getenv("GOOGLE_ACCOUNT_JSON_BASE64")):
            service_base_creds = os.environ["GOOGLE_ACCOUNT_JSON_BASE64"]
            logger.info("""Default service credentials found""")

        else:

            # pull creds from gcloud sdk
            user_creds, _ = google.auth.default()
            project_name = user_creds.quota_project_id

            # try getting service account creds
            try:
                logger.info(
                    """No default opsml creds found. Loading from secret %s and project %s.""",
                    service_account_secret_name,
                    project_name,
                )  # noqa

                service_base_creds = OpsmlCreds.get_secret_from_gcp(
                    user_creds=user_creds,
                    service_account_secret_name=service_account_secret_name,
                    project_name=project_name,
                )

            # this is for instances where there is no service account.
            # Defaulting to user creds
            # soft failure
            except Exception as error:
                logger.error(f"{error}")
                raise error

        base_64 = base64.b64decode(s=service_base_creds).decode("utf-8")
        key = json.loads(base_64)

        logger.info("Setting gcp credentials")
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key)  # noqa
        project_id: str = service_creds.project_id

        logger.info("GCP project: %s", project_id)

        return service_creds, project_id  # type: ignore


@dataclass
class Defaults:
    """Default kwargs that are passed to some operations,
    but can be overridden.
    """

    _singleton: ClassVar[Any] = None
    PATH: str = os.getcwd()
    RUN_ID: str = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    APP_ENV: str = os.getenv("ENV", "staging")

    def __post_init__(self):
        secret_name = f"opsml_service_creds_{self.APP_ENV}"
        self.GCP_CREDS, self.GCP_PROJECT = OpsmlCreds.set_opsml_creds(
            service_account_secret_name=secret_name,
        )
        self.SERVICE_ACCOUNT = getattr(
            self.GCP_CREDS,
            "service_account_email",
            None,
        )

        # env specific secrets
        self._load_env_vars(
            vars_=[
                "gcp_region",
                "gcs_bucket",
                "snowflake_api_auth",
                "snowflake_api_url",
                "db_name",
                "db_instance_name",
                "db_username",
                "db_password",
            ],
            secrets=[
                "gcp_pipeline_region",
                "gcs_pipeline_bucket",
                "snowflake_api_auth",
                "snowflake_api_url",
                "data_registry_db_name",
                "data_registry_instance_name",
                "data_registry_username",
                "data_registry_password",
            ],
        )

    def _load_env_vars(
        self,
        vars_: List[str],
        secrets: List[str],
    ):
        """Loads env vars from gcp secret manager project depending on APP_ENV.

        Args:
            vars_ (List): List of vars to set
            secrets: (List): List of corresponding secret names
        """
        secret_client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=self.GCP_CREDS,
        )
        for var, secret in zip(vars_, secrets):
            value = secret_client.get_secret(
                project=self.GCP_PROJECT,
                secret=secret,
            )

            setattr(self, var, value)

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = super().__new__(cls, *args, **kwargs)
        return cls._singleton


DEFAULTS = Defaults()

params = Params(**{k.lower(): v for k, v in DEFAULTS.__dict__.items()})


class SnowflakeCredentials:
    @staticmethod
    def credentials() -> SnowflakeParams:
        login_vars = {}
        secret_client = GCPClient.get_service(
            service_name="secret_manager",
            gcp_credentials=params.gcp_creds,
        )
        for secret in SnowflakeParams.__annotations__.keys():  # pylint: disable=no-member
            value = secret_client.get_secret(
                project=params.gcp_project,
                secret=f"snowflake_{secret}",
            )

            login_vars[secret] = value

        return SnowflakeParams(**login_vars)
