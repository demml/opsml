from typing import cast

from pydantic import BaseModel

from opsml_artifacts.helpers.gcp_utils import (
    GCPClient,
    GcpCredsSetter,
    GCPSecretManager,
)

creds = GcpCredsSetter().get_creds()


class SnowflakeParams(BaseModel):
    """Loads snowflake credentials from gcs"""

    username: str
    password: str
    host: str
    database: str
    warehouse: str
    role: str
    api_auth: str
    api_url: str

    class Config:
        extra = "allow"


class SnowflakeCredentials:
    @staticmethod
    def credentials() -> SnowflakeParams:
        login_vars = {}
        secret_client = cast(
            GCPSecretManager,
            GCPClient.get_service(
                service_name="secret_manager",
                gcp_credentials=creds.creds,
            ),
        )

        for secret in SnowflakeParams.__annotations__.keys():  # pylint: disable=no-member
            value = secret_client.get_secret(
                project_name=creds.project,
                secret=f"snowflake_{secret}",
            )
            login_vars[secret] = value
        login_vars["gcp_creds"] = creds.creds
        login_vars["gcp_project"] = creds.project
        return SnowflakeParams(**login_vars)
