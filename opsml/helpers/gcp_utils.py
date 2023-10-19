# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import os
from typing import Optional, Tuple, Union, cast

import google.auth
from google.auth.credentials import Credentials
from google.cloud import storage  # type: ignore
from google.oauth2 import service_account
from pydantic import BaseModel, ConfigDict

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class GcpCreds(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    creds: Optional[Credentials] = None
    project: Optional[str] = None


class GCPService:
    def __init__(
        self,
        gcp_credentials: Optional[Credentials] = None,
    ):
        """Generic init"""

    @staticmethod
    def valid_service_name(service_name: str) -> bool:
        """Validates service name"""
        raise NotImplementedError


class GCSStorageClient(GCPService):
    def __init__(
        self,
        gcp_credentials: Optional[Credentials] = None,
    ):
        """Instantiates GCP storage client

        Args:
            gcp_credentials (Credentials): Credentials with permissions for
            gcp storage client

        """
        self.client = storage.Client(credentials=gcp_credentials)

    def list_objects(
        self,
        gcs_bucket: Union[str, None] = None,
        prefix: Union[str, None] = None,
    ):
        """List object is a given bucket with the specified prefix

        Args:
            gcs_bucket (str): Name of GCS bucket
            prefix (str): Blob prefix

        Returns:
            List of storage blobs

        """
        bucket = self.client.bucket(gcs_bucket)
        blobs = bucket.list_blobs(prefix=prefix)
        return blobs

    def download_object(
        self,
        gcs_bucket: str,
        blob_path: Union[str, None] = None,
        destination_filename: Union[str, None] = None,
    ):
        """Download an object from gcs

        Args:
            gcs_bucket (str): Name of GCS bucket
            blob_path (str): Path to object in gcs (including object name)
            destination_filename (str): Local filename to download to.

        """

        bucket = self.client.bucket(gcs_bucket)
        blob = bucket.blob(blob_path)
        blob.download_to_filename(destination_filename)

        logger.info("Successfully downloaded gs://{}/{}", gcs_bucket, blob_path)

    def download_object_from_uri(self, gcs_uri: str):
        bucket, blob, filename = self.parse_gcs_uri(gcs_uri=gcs_uri)

        self.download_object(
            gcs_bucket=bucket,
            blob_path=blob,
            destination_filename=filename,
        )

        return filename

    def delete_object(
        self,
        gcs_bucket: str,
        blob_path: Union[str, None] = None,
    ):
        """Delete object from gcs

        Args:
            gcs_bucket:
                Name of GCS bucket
            blob_path:
                Path to object in gcs (including object name)

        """

        bucket = self.client.bucket(gcs_bucket)
        blob = bucket.blob(blob_path)
        blob.delete()

        logger.info("Successfully deleted gs://{}/{}", gcs_bucket, blob_path)

    def parse_gcs_uri(
        self,
        gcs_uri: str,
    ):
        """Parses gcs url

        Args:
            gcs_uri:
                Uri for gcs object

        Return:
            gcs_bucket blob_path and filename
        """

        split_url = gcs_uri.split("/")
        bucket = split_url[2]
        blob_path = "/".join(split_url[3:])
        filename = split_url[-1]

        return bucket, blob_path, filename

    def delete_object_from_url(self, gcs_uri: str):
        """Delete object from gcs

        Args:
            gcs_uri:
                GCS uri of object

        """

        bucket, blob_path, _ = self.parse_gcs_uri(
            gcs_uri,
        )

        self.delete_object(
            bucket,
            blob_path,
        )

    def upload(
        self,
        gcs_bucket: str,
        filename: str,
        destination_path: str,
    ):
        """Upload local file to gcs

        Args:
            gcs_bucket:
                Name of gcs bucket
            filename:
                Local filename to upload
            destination_path:
                gcs path to write to

        Returns:
            Location of gcs object

        """

        bucket = self.client.bucket(gcs_bucket)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(filename)
        gcs_uri = f"gs://{gcs_bucket}/{destination_path}"

        logger.info("Uploaded {} to {}", filename, gcs_uri)

        return gcs_uri

    @staticmethod
    def valid_service_name(service_name: str):
        return bool(service_name == "storage")


ClientTypes = GCSStorageClient


class GCPClient:
    @staticmethod
    def get_service(
        service_name: str,
        gcp_credentials: Optional[Credentials] = None,
    ) -> ClientTypes:
        service = next(
            service
            for service in GCPService.__subclasses__()
            if service.valid_service_name(
                service_name=service_name,
            )
        )
        return cast(ClientTypes, service(gcp_credentials=gcp_credentials))


class GcpCredsSetter:
    def __init__(self, service_creds: Optional[str] = None):
        """Set credentials"""

        self.service_base64_creds = service_creds or os.environ.get("GOOGLE_ACCOUNT_JSON_BASE64")  # type: ignore

    def get_creds(self) -> GcpCreds:
        service_creds, project_name = self.get_base64_creds()

        return GcpCreds(
            creds=service_creds,
            project=project_name,
        )

    def get_base64_creds(self) -> Tuple[Optional[Credentials], Optional[str]]:
        if not self.has_service_base64_creds:
            return self.get_gcp_sdk_creds()

        return self.create_gcp_creds_from_base64(
            service_base64_creds=str(
                self.service_base64_creds,
            )
        )

    @property
    def has_service_base64_creds(self) -> bool:
        """Has environment creds"""
        return bool(self.service_base64_creds)

    def get_gcp_sdk_creds(self) -> Tuple[Optional[Credentials], Optional[str]]:
        """Pulls google cloud sdk creds from local env

        Returns
            Tuple containing user credentials and project name
        """
        user_creds, _ = google.auth.default()
        if user_creds is None:
            logger.info("No gcp credentials found. Using defaults")

        project_name = user_creds.quota_project_id

        return user_creds, project_name

    def decode_base64(self, service_base64_creds: str) -> str:
        base_64 = base64.b64decode(s=service_base64_creds).decode("utf-8")
        return json.loads(base_64)

    def create_gcp_creds_from_base64(self, service_base64_creds: str) -> Tuple[Credentials, Optional[str]]:
        """Decodes base64 encoded service creds into GCP Credentials

        Returns
            Tuple of gcp credentials and project name
        """
        key = self.decode_base64(service_base64_creds=service_base64_creds)
        service_creds: Credentials = service_account.Credentials.from_service_account_info(info=key)  # noqa
        project_name = service_creds.project_id

        return service_creds, project_name
