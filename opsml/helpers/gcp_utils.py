# mypy: disable-error-code="attr-defined"


# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import os
from typing import Optional, Tuple, cast

from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pydantic import BaseModel, ConfigDict

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class GcpCreds(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    creds: Optional[Credentials] = None
    project: Optional[str] = None


class GcpCredsSetter:
    def __init__(self, service_creds: Optional[str] = None) -> None:
        """Set credentials"""

        self.service_base64_creds = service_creds or os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")

    def get_creds(self) -> GcpCreds:
        service_creds, project_name = self.get_base64_creds()

        return GcpCreds(
            creds=service_creds,
            project=project_name,
        )

    def get_base64_creds(self) -> Tuple[Optional[Credentials], Optional[str]]:
        if self.service_base64_creds is not None:
            logger.info("Using base64 encoded service creds")
            return self.create_gcp_creds_from_base64(self.service_base64_creds)

        return (None, None)

    def decode_base64(self, service_base64_creds: str) -> str:
        base_64 = base64.b64decode(s=service_base64_creds).decode("utf-8")
        return cast(str, json.loads(base_64))

    def create_gcp_creds_from_base64(self, service_base64_creds: str) -> Tuple[Credentials, Optional[str]]:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name
        """
        scopes = {"scopes": ["https://www.googleapis.com/auth/devstorage.full_control"]}  # needed for gcsfs
        key = self.decode_base64(service_base64_creds=service_base64_creds)
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key, **scopes)  # noqa
        project_name = cast(str, service_creds.project_id)

        return service_creds, project_name
