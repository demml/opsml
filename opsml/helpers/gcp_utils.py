# mypy: disable-error-code="attr-defined"


# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import os
from typing import Optional, Tuple, Union, cast, Dict, Any

import google.auth
from google.auth import compute_engine
from google.auth.compute_engine.credentials import (
    Credentials as ComputeEngineCredentials,
)
from google.auth.identity_pool import Credentials as IdentityPoolCredentials
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from pydantic import BaseModel, ConfigDict, model_validator

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class GcpCreds(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    creds: Optional[
        Union[
            Credentials,
            compute_engine.IDTokenCredentials,
            ComputeEngineCredentials,
            IdentityPoolCredentials,
        ]
    ] = None
    project: Optional[str] = None
    default_creds: bool = False
    service_account: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        base64_creds = os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")

        # load service account from base64
        if base64_creds:
            logger.info("Using base64 encoded service creds")
            model_args["service_account"] = cls.decode_base64(service_base64_creds=base64_creds)

        # check for service account file
        service_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_SA")

        if service_account_file:
            logger.info("Using service account file")
            with open(service_account_file, "r") as f:
                service_account = json.load(f)
                model_args["service_account"] = service_account
                print(service_account.keys())

        return model_args

    @classmethod
    def decode_base64(cls, service_base64_creds: str) -> str:
        base_64 = base64.b64decode(s=service_base64_creds).decode("utf-8")
        return cast(str, json.loads(base_64))


class GcpCredsSetter:
    def __init__(self) -> None:
        """Set credentials"""

        self.creds = GcpCreds()

    def get_creds(self) -> GcpCreds:
        self._get_creds()

        return self.creds

    def _get_creds(self) -> None:
        """Get GCP credentials

        Returns:
            Tuple of gcp credentials and project name, and whether default credentials are used
        """
        if self.creds.service_account is not None:
            logger.info("Authenticating with service account")
            return self.create_gcp_creds_from_sa()

        logger.info("Authenticating with default credentials")
        return self.get_default_creds()

    def get_default_creds(self) -> None:
        credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/devstorage.full_control"])  # type: ignore

        self.creds.project = project_id
        self.creds.creds = credentials
        self.creds.default_creds = True

    def create_gcp_creds_from_sa(self) -> None:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name, and whether default credentials are used
        """

        scopes = {"scopes": ["https://www.googleapis.com/auth/devstorage.full_control"]}  # needed for gcsfs

        print(self.creds.service_account["type"])  # type: ignore # noqa
        service_creds = IdentityPoolCredentials.from_info(self.creds.service_account, **scopes)  # type: ignore # noqa
        print("hello")

        service_creds: Credentials = service_account.Credentials.from_service_account_info(  # type: ignore # noqa
            info=self.creds.service_account,
            **scopes,
        )
        project_name = cast(str, service_creds.project_id)

        self.creds.project = project_name
        self.creds.creds = service_creds
        self.creds.default_creds = False
