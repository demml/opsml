import json
import os
import pathlib
from enum import Enum
from functools import cached_property
from typing import Any, Dict, Union

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiClient, ApiRoutes

logger = ArtifactLogger.get_logger(__name__)

TRACKING_URI = str(os.environ.get("OPSML_TRACKING_URI"))
_METADATA_FILENAME = "metadata.json"


# this is a duplicate of opsml/registry/sql/sql_schema
# This is done in order to avoid instantiating DefaultSettings when using CLI (saves time)
class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    RUN = os.getenv("ML_RUN_REGISTRY_NAME", "OPSML_RUN_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")
    PROJECT = os.getenv("ML_PROJECT_REGISTRY_NAME", "OPSML_PROJECT_REGISTRY")


class CliApiClient:
    @cached_property
    def client(self) -> ApiClient:
        return ApiClient(base_url=TRACKING_URI)

    def download_metadata(self, payload: Dict[str, str], path: pathlib.Path) -> Dict[str, Any]:
        """
        Loads and saves model metadata

        Args:
            request_client:
                `ApiClient`
            payload:
                Payload to pass to request client
            path:
                Pathlib path to save response to

        Returns:
            Dictionary of metadata
        """

        metadata = self.client.stream_post_request(
            route=ApiRoutes.DOWNLOAD_MODEL_METADATA,
            json=payload,
        )

        metadata_path = path / _METADATA_FILENAME
        logger.info("saving metadata to %s", str(metadata_path))
        metadata_path.write_text(json.dumps(metadata, indent=4))

        return metadata

    def download_model(self, filepath: str, write_path: pathlib.Path) -> None:
        """
        Downloads model file to directory

        Args:
            request_client:
                `ApiClient`
            filepath:
                External model filepath
            write_path:
                Path to write file to

        """

        filepath_split = filepath.split("/")
        filename = filepath_split[-1]
        read_dir = "/".join(filepath_split[:-1])

        logger.info("saving model to %s", str(write_path))
        self.client.stream_download_file_request(
            route=ApiRoutes.DOWNLOAD_FILE,
            local_dir=str(write_path),
            filename=filename,
            read_dir=read_dir,
        )

    def list_cards(self, payload: Dict[str, Union[str, int]]):
        response = self.client.post_request(
            route=ApiRoutes.LIST_CARDS,
            json=payload,
        )

        return response.get("cards")
