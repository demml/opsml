from google.oauth2.service_account import Credentials
from pydantic import BaseModel, Extra


class Params(BaseModel):
    """Creates pipeline params associated
    with the current pipeline run.
    """

    gcp_project: str
    gcs_bucket: str
    gcp_region: str
    run_id: str
    app_env: str
    gcp_creds: Credentials
    snowflake_api_auth: str
    snowflake_api_url: str

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True
