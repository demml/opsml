from typing import Optional, Union, cast

from google.cloud import secretmanager, storage  # type: ignore
from google.oauth2.service_account import Credentials
from pyshipt_logging import ShiptLogging

logger = ShiptLogging.get_logger(__name__)


class GCPService:
    def __init__(
        self,
        gcp_credentials: Optional[Credentials] = None,
    ):
        """Generic init"""

    @staticmethod
    def valid_service_name(service_name: str):
        """Validates service name"""


class GCPSecretManager(GCPService):
    def __init__(
        self,
        gcp_credentials: Optional[Credentials] = None,
    ):
        """Class for interacting with GCP secrets related to
        a project.

        Args:
            gcp_credentials (gcp Credentials): Credentials associated with
            a given gcp account that has permissions for accessing secrets.
            If not supplied, gcp will infer credentials for you local environment.
        """
        self.client = secretmanager.SecretManagerServiceClient(
            credentials=gcp_credentials,
        )

    def get_secret(
        self,
        project_name: str,
        secret: str,
        version: str = "latest",
    ):

        """Gets secret for GCP secrets manager.

        Args:
            project (str): GCP Project
            secret (str): Name of secret
            version (str) Version of secret to pull

        Returns
            secret value

        """

        response = self.client.access_secret_version(
            request={"name": f"projects/{project_name}/secrets/{secret}/versions/{version}"}  # noqa
        )

        payload = response.payload.data.decode("UTF-8")

        return payload

    @staticmethod
    def valid_service_name(service_name: str):
        return bool(service_name == "secret_manager")


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
        self.client = storage.Client(
            credentials=gcp_credentials,
        )

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

        logger.info("Successully downloaded gs://%s/%s", gcs_bucket, blob_path)

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
            gcs_bucket (str): Name of GCS bucket
            blob_path (str): Path to object in gcs (including object name)

        """

        bucket = self.client.bucket(gcs_bucket)
        blob = bucket.blob(blob_path)
        blob.delete()

        logger.info("Successully deleted gs://%s/%s", gcs_bucket, blob_path)

    def parse_gcs_uri(
        self,
        gcs_uri: str,
    ):
        """Parses gcs url

        Args:
            gcs_uri (str): Uri for gcs object

        Return:
            gcs_bucket and path
        """

        split_url = gcs_uri.split("/")
        bucket = split_url[2]
        blob_path = "/".join(split_url[3:])
        filename = split_url[-1]

        return bucket, blob_path, filename

    def delete_object_from_url(self, gcs_uri: str):

        """Delete object from gcs

        Args:
            gcs_uri (str): GCS uri of object

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
            gcs_bucket (str): Name of gcs bucket
            filename (str): Local filename to upload
            destination_path (str): gcs path to write to

        Returns:
            Location of gcs object

        """
        bucket = self.client.bucket(gcs_bucket)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(filename)
        gcs_uri = f"gs://{gcs_bucket}/{destination_path}"

        logger.info("Uploaded %s to %s", filename, gcs_uri)

        return gcs_uri

    @staticmethod
    def valid_service_name(service_name: str):
        return bool(service_name == "storage")


ClientTypes = Union[GCPSecretManager, GCSStorageClient]


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
