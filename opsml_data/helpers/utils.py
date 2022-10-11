import base64
import json
from google.oauth2 import service_account
from functools import cached_property


class GCPCredentials:
    def __init__(self, gcp_creds: str):

        if gcp_creds == None:
            raise ValueError("GCP Creds must not be None.")

        base_64 = base64.b64decode(gcp_creds).decode("utf-8")
        self.key = json.loads(base_64)

    @cached_property
    def credentials(self):
        return service_account.Credentials.from_service_account_info(self.key)
