# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional, Union
from opsml.app.core.dependencies import swap_opsml_root

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt

from opsml.helpers.logging import ArtifactLogger
from opsml.storage.client import StorageClient
from opsml.types import ModelMetadata
from opsml.storage import client

logger = ArtifactLogger.get_logger()

ModelSettingsType = Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]


class RegistrationError(Exception):
    pass


class RegistrationRequest(BaseModel):
    name: str
    version: str
    onnx: bool


class ModelRegistrar:
    """Class used to register models to a well known URIs.

    Registration is the process of "promoting" or "registering" a model into a
    well known URI separate from model artifacts. Models must be registered
    before they are hosted. Once registered, the model is guaranteed not to be
    moved or deleted from the registered URI.
    """

    def __init__(
        self,
        storage_client: StorageClient,
    ):
        """Instantiates Registrar class

        Args:
            storage_client: The storage client used to register models.
        """
        if storage_client is None:
            raise ValueError("storage_client is required")
        self.storage_client = storage_client

    def _registry_path(self, request: RegistrationRequest) -> Path:
        """Returns hardcoded uri"""
        return Path(f"model_registry/{request.name}/v{request.version}")

    def is_registered(self, request: RegistrationRequest) -> bool:
        """Checks if registry path is empty.

        You can call `is_registered` before attempting to register a model, but
        it's not required. Attempting to register a model that's already been
        registered will overwrite the currently registered model.

        Args:
            request: The model registration request.
        """
        path = self._registry_path(request)
        files = self.storage_client.find(path)
        return bool(files)

    def _get_correct_model_uri(self, request: RegistrationRequest, metadata: ModelMetadata) -> str:
        """Gets correct model uri based on the request's onnx flag.

        Args:
            request: The model registration request.
            metadata: The model metadata.
        """
        if request.onnx:
            if metadata.onnx_uri is None:
                raise RegistrationError("the onnx model uri does not exist")
            return metadata.onnx_uri
        return metadata.model_uri

    @retry(reraise=True, stop=stop_after_attempt(3))
    def _copy_model_to_registry(
        self,
        request: RegistrationRequest,
        model_uri: Path,
        metadata: ModelMetadata,
    ) -> Path:
        """Copies a model from it's original storage path to a hardcoded model registry path

        Args:
            request: The registration request
            model_uri: The model URI to register for the request.

        Returns:
            The URI to the directory containing the registered model.

        """

        read_path = model_uri.parent
        registry_path = self._registry_path(request)

        # delete existing model if it exists
        if self.is_registered(request):
            logger.info("Model detected in registry path. Deleting: {}", registry_path)
            self.storage_client.rm(registry_path)
            assert not self.is_registered(request)

        # register the model
        self.storage_client.copy(read_path, registry_path, False)

        # register model settings
        self.register_model_settings(metadata, registry_path, model_uri)

        if not self.is_registered(request):
            raise RegistrationError("Failed to copy model to registered URL")

        return registry_path

    def _model_settings(self, metadata: ModelMetadata, model_uri: str) -> ModelSettingsType:
        """Create standard dictionary for model-settings.json file

        Args:
            metadata:
                The model metadata.

            model_uri:
                The URI to the model.

        Returns:
            A dictionary containing the model settings.
        """

        # remove dashes for downstream compatibility
        return {
            "name": metadata.model_name.replace("-", "_"),
            "implementation": "models.OnnxModel",
            "parameters": {
                "uri": f"./{Path(model_uri).name}",
                "extra": {
                    "model_version": metadata.model_version,
                    "opsml_name": metadata.model_name.replace("-", "_"),
                },
            },
        }

    def register_model_settings(self, metadata: ModelMetadata, registry_path: str, model_uri: str) -> None:
        """Generate a model-settings.json file for Seldon custom server

        Args:
            metadata:
                The model metadata.
            registry_path:
                The path to the registered model.
            model_uri:
                The URI to the model.
        """

        model_settings = self._model_settings(metadata, model_uri)
        logger.info("ModelRegistrar: registering model settings: {}", model_settings)
        with tempfile.TemporaryDirectory() as tmpdirname:
            lpath = Path(tmpdirname) / "model-settings.json"
            lpath.write_text(json.dumps(model_settings))
            self.storage_client.put(lpath, Path(registry_path))

        logger.info("ModelRegistrar: registered model settings: {} path={}", model_settings, registry_path)

    def register_model(self, request: RegistrationRequest, metadata: ModelMetadata) -> Path:
        """Registers a model to a hardcoded storage path.

        Args:
            request: Registration request
            metadata: Associated model metadata

        Returns:
            The URI to the directory containing the registered model.
        """
        model_uri = swap_opsml_root(self._get_correct_model_uri(request, metadata))

        logger.info("ModelRegistrar: registering model: {}", request.model_dump())
        registry_path = self._copy_model_to_registry(request, Path(model_uri), metadata)
        logger.info("ModelRegistrar: registered model: {} path={}", request.model_dump(), registry_path)

        return registry_path
