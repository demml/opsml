# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import pathlib
from enum import Enum
from functools import cached_property
from typing import Any, Dict, List, Tuple, Union, cast

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiClient, ApiRoutes

logger = ArtifactLogger.get_logger()

TRACKING_URI = str(os.environ.get("OPSML_TRACKING_URI")).strip("/")  # strip trailing slash if it has one
_METADATA_FILENAME = "metadata.json"
_DATA_PROFILE_FILENAME = "data_profile.html"


# Duplicate enum
# This is done in order to avoid instantiating DefaultSettings when using CLI (saves time)

Metrics = Dict[str, List[Dict[str, Union[float, int, str]]]]
BattleReports = List[Any]
MetricReport = Dict[str, BattleReports]


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
        Downloads model metadata to directory

        Args:
            payload:
                Payload to send to API
            path:
                Pathlib path to save response to

        Returns:
            Metadata
        """

        metadata = self.client.post_request(
            route=ApiRoutes.MODEL_METADATA,
            json=payload,
        )

        metadata_path = path / _METADATA_FILENAME
        logger.info("saving metadata to {}", metadata_path)
        metadata_path.write_text(json.dumps(metadata, indent=4))

        return metadata

    def download_model(self, filepath: str, write_path: pathlib.Path) -> None:
        """
        Downloads model file to directory

        Args:
            filepath:
                External model filepath
            write_path:
                Path to write file to
        """

        filepath_split = filepath.split("/")
        filename = filepath_split[-1]
        read_dir = "/".join(filepath_split[:-1])

        logger.info("saving model to {}", write_path)
        self.client.stream_download_file_request(
            route=ApiRoutes.DOWNLOAD_FILE,
            local_dir=str(write_path),
            filename=filename,
            read_dir=read_dir,
        )

    def list_cards(self, payload: Dict[str, Union[str, int, Dict[str, str]]]):
        response = self.client.post_request(
            route=ApiRoutes.LIST_CARDS,
            json=payload,
        )

        return response.get("cards")

    def get_metrics(self, payload: Dict[str, Union[str, int]]) -> Metrics:
        response = self.client.post_request(
            route=ApiRoutes.MODEL_METRICS,
            json=payload,
        )

        metrics = cast(Metrics, response.get("metrics"))
        return metrics

    def compare_metrics(self, payload: Dict[str, Union[str, int, bool, List[str]]]) -> Tuple[str, str, MetricReport]:
        response = self.client.post_request(
            route=ApiRoutes.COMPARE_MODEL_METRICS,
            json=payload,
        )

        metric_report = cast(MetricReport, response.get("report"))
        challenger_name = str(response.get("challenger_name"))
        challenger_version = str(response.get("challenger_version"))

        return challenger_name, challenger_version, metric_report

    def stream_data_file(
        self,
        path: str,
        payload: Dict[str, Union[str, int, List[str]]],
        write_path: pathlib.Path,
    ) -> None:
        """
        Streams data file to directory

        Args:
            path:
                write path
            payload:
                Payload to pass to request client
            write_path:
                Path to write file to

        """
        with open(os.path.join(write_path, _DATA_PROFILE_FILENAME), "wb") as local_file:
            with self.client.client.stream(
                method="POST",
                url=f"{self.client.base_url}/{path}",
                json=payload,
            ) as response:
                for data in response.iter_bytes():
                    local_file.write(data)

            if response.status_code != 200:
                response_result = json.loads(data.decode("utf-8"))  # pylint: disable=undefined-loop-variable

                raise ValueError(
                    f"""Failed to to make server call for post request Url: {path}.
                    {response_result.get("detail")}
                    """
                )
