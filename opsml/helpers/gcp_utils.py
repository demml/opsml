# mypy: disable-error-code="attr-defined"


# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import os
from typing import Optional, Tuple, Union, cast

import google.auth
from google.auth import compute_engine
from google.auth.compute_engine.credentials import (
    Credentials as ComputeEngineCredentials,
)
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pydantic import BaseModel, ConfigDict

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class GcpCreds(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    creds: Optional[Union[Credentials, compute_engine.IDTokenCredentials, ComputeEngineCredentials]] = None
    project: Optional[str] = None
    default_creds: bool = False


class GcpCredsSetter:
    def __init__(self, service_creds: Optional[str] = None) -> None:
        """Set credentials"""

        self.service_base64_creds = service_creds or os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")

    def get_creds(self) -> GcpCreds:
        service_creds, project_name, default_creds = self._get_creds()

        return GcpCreds(creds=service_creds, project=project_name, default_creds=default_creds)

    def _get_creds(self) -> Tuple[Optional[Union[ComputeEngineCredentials, Credentials]], Optional[str], bool]:
        """Get GCP credentials

        Returns:
            Tuple of gcp credentials and project name, and whether default credentials are used
        """
        if self.service_base64_creds is not None:
            logger.info("Using base64 encoded service creds")
            return self.create_gcp_creds_from_base64(self.service_base64_creds)

        logger.info("Using default creds")
        return self.get_default_creds()

    def get_default_creds(self) -> Tuple[Optional[ComputeEngineCredentials], Optional[str], bool]:
        credentials, project_id = google.auth.default()

        return credentials, project_id, True

    def decode_base64(self, service_base64_creds: str) -> str:
        base_64 = base64.b64decode(s=service_base64_creds).decode("utf-8")
        return cast(str, json.loads(base_64))

    def create_gcp_creds_from_base64(self, service_base64_creds: str) -> Tuple[Credentials, Optional[str], bool]:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name, and whether default credentials are used
        """
        scopes = {"scopes": ["https://www.googleapis.com/auth/devstorage.full_control"]}  # needed for gcsfs
        key = self.decode_base64(service_base64_creds=service_base64_creds)
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key, **scopes)  # noqa
        project_name = cast(str, service_creds.project_id)

        return service_creds, project_name, False
