import base64
import json
from turtle import st
from google.oauth2 import service_account
from functools import cached_property
from .defaults import defaults
from pyshipt_logging import ShiptLogging
from google.cloud import storage

logger = ShiptLogging.get_logger(__name__)


class GCPCredentials:
    def __init__(self, gcp_creds: str):

        if gcp_creds == None:
            raise ValueError("GCP Creds must not be None.")

        base_64 = base64.b64decode(gcp_creds).decode("utf-8")
        self.key = json.loads(base_64)

    @cached_property
    def credentials(self):
        return service_account.Credentials.from_service_account_info(self.key)


class GCSStorageClient:
    def __init__(self, gcs_bucket: str):
        self.credentials = self.get_creds()
        self.bucket = self.set_storage_bucket(gcs_bucket)

    def get_creds(self):

        if defaults.GCP_CREDS is not None:
            base_64 = base64.b64decode(
                defaults.GCP_CREDS,
            )
            key = json.loads(
                base_64.decode("utf-8"),
            )

            return service_account.Credentials.from_service_account_info(  # noqa
                key,
            )

        else:
            return None

    def list_objects(
        self,
        prefix: str = None,
    ):
        blobs = self.bucket.list_blobs(prefix=prefix)
        blobs = [blob.name for blob in blobs]
        return blobs

    def set_storage_bucket(
        self,
        gcs_bucket: str = None,
    ):
        storage_client = storage.Client(
            credentials=self.credentials,
        )

        bucket = storage_client.bucket(gcs_bucket)
        if not bucket.exists():
            bucket.create()

        return bucket

    def download_object(
        self,
        blob_path: str = None,
        destination_filename: str = None,
    ):
        blob = self.bucket.blob(blob_path)
        blob.download_to_filename(destination_filename)

        logger.info(
            f"Successully downloaded gs://{self.bucket.name}/{blob_path}",
        )

    def delete_object(
        self,
        blob_path: str = None,
    ):
        blob = self.bucket.blob(blob_path)
        blob.delete()

        logger.info(
            f"Successully deleted gs://{self.bucket.name}/{blob_path}",
        )

    def parse_gcs_url(
        self,
        gcs_url: str,
    ):
        split_url = gcs_url.split("/")
        bucket = split_url[2]
        blob_path = "/".join(split_url[3:])

        return bucket, blob_path

    def delete_object_from_url(self, gcs_url: str):
        bucket, blob_path = self.parse_gcs_url(
            gcs_url,
        )

        self.delete_object(
            blob_path,
        )
