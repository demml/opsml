"""Suite of helper objects"""
import glob
import os
from pathlib import Path
from typing import Optional, Union

from google.cloud import secretmanager, storage  # type: ignore
from google.oauth2.service_account import Credentials
from pyshipt_logging import ShiptLogging

from . import exceptions

logger = ShiptLogging.get_logger(__name__)


class FindPath:
    """Helper class for finding paths to artifacts"""

    @staticmethod
    def find_filepath(
        name: str,
        path: Optional[str] = None,
    ) -> Path:
        """Finds the file path of a given file.

        Args:
            name (str): Name of file
            path (str): Optional. Base path to search

        Returns:
            filepath (str)
        """
        if path is None:
            path = os.getcwd()

        paths = list(Path(path).rglob(name))
        file_path = paths[0]

        if file_path is not None:
            return file_path

        raise exceptions.MissingKwarg(
            f"""{name} file was not found in the current path.
                    Check to make sure you specified the correct name."""
        )

    @staticmethod
    def find_dirpath(
        dir_name: str,
        path: str,
        anchor_file: str,
    ):
        """Finds the dir path of a given file.
        Used as part of pipeline runner.

        Args:
            dir_name (str): Name of directory
            path (str): Optional. Base path to search
            anchor_file (str): Name of anchor file in directory

        Returns:
            dirpath (str)
        """

        paths = glob.glob(f"{path}/**/{anchor_file}", recursive=True)

        if len(paths) <= 1:
            new_path: Union[list, str] = []
            dirs = paths[0].split("/")[:-1]

            try:
                dir_idx = dirs.index(dir_name)
            except ValueError as error:
                raise exceptions.DirNotFound(
                    f"""Directory {dir_name} was not found.
                     Please check the name of your top-level directory.
                     Error: {error}
                     """
                )

            new_path = "/".join(dirs[: dir_idx + 1])

            logger.info("Src dir path: %s", new_path)
            return new_path

        raise exceptions.MoreThanOnePath(
            f"""More than one path was found for the trip configuration file.
                Please check your project structure.
                Found paths: {paths}
            """
        )

    @staticmethod
    def find_source_dir(
        path: str,
        runner_file: str,
    ):
        """Finds the dir path of a given of the pipeline
        runner file.

        Args:
            path (str): Current directory
            runner_file (str): Name of pipeline runner file

        Returns:
            dirpath (str)
        """
        paths = glob.glob(f"{path}/**/{runner_file}", recursive=True)
        if len(paths) <= 1:
            source_path = "/".join(paths[0].split("/")[:-1])
            source_dir = paths[0].split("/")[:-1][-1]
            return source_dir, source_path

        raise exceptions.MoreThanOnePath(
            f"""More than one path was found for the trip configuration file.
                Please check your project structure.
                Found paths: {paths}
            """
        )


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


class GCPClient:
    @staticmethod
    def get_service(
        service_name: str,
        gcp_credentials: Optional[Credentials] = None,
    ):

        service = next(
            service
            for service in GCPService.__subclasses__()
            if service.valid_service_name(
                service_name=service_name,
            )
        )
        return service(gcp_credentials=gcp_credentials)
