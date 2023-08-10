# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Optional

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt

from opsml.helpers.logging import ArtifactLogger
from opsml.model.types import ModelMetadata
from opsml.registry.storage.storage_system import StorageClientType

logger = ArtifactLogger.get_logger(__name__)


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
        storage_client: StorageClientType,
    ):
        """Instantiates Registrar class

        Args:
            storage_client: The storage client used to register models.
        """
        if storage_client is None:
            raise ValueError("storage_client is required")
        self.storage_client = storage_client

    def _registry_path(self, request: RegistrationRequest) -> str:
        """Returns hardcoded uri"""
        return f"{self.storage_client.base_path_prefix}/model_registry/{request.name}/v{request.version}"

    def is_registered(self, request: RegistrationRequest) -> bool:
        """Checks if registry path is empty.

        You can call `is_registered` before attempting to register a model, but
        it's not required. Attempting to register a model that's already been
        registered will overwrite the currently registered model.

        Args:
            request: The model registration request.
        """

        try:
            path = self._registry_path(request)
            files = self.storage_client.list_files(path)

            if len(files) == 0 or files[0] == path:
                # no files or only an empty directory exists
                return False

            return True
        except FileNotFoundError:
            return False

    def _get_correct_model_uri(self, request: RegistrationRequest, metadata: ModelMetadata) -> Optional[str]:
        """Gets correct model uri based on the request's onnx flag.

        Args:
            request: The model registration request.
            metadata: The model metadata.
        """
        if request.onnx:
            return metadata.onnx_uri
        return metadata.model_uri

    @retry(reraise=True, stop=stop_after_attempt(3))
    def _copy_model_to_registry(self, request: RegistrationRequest, model_uri: str):
        """Copies a model from it's original storage path to a hardcoded model registry path

        Args:
            request: The registration request
            model_uri: The model URI to register for the request.

        Returns:
            The URI to the directory containing the registered model.

        """
        read_path = os.path.dirname(model_uri)
        registry_path = self._registry_path(request)

        # delete existing model if it exists
        if self.is_registered(request):
            logger.info("Model detected in registry path. Deleting: %s", registry_path)
            self.storage_client.delete(registry_path)
            assert not self.is_registered(request)

        # register the model
        self.storage_client.copy(read_path=read_path, write_path=registry_path)

        if not self.is_registered(request):
            raise RegistrationError("Failed to copy model to registered URL")

        return registry_path

    def register_model(self, request: RegistrationRequest, metadata: ModelMetadata) -> str:
        """Registers a model to a hardcoded storage path.

        Args:
            request: Registration request
            metadata: Associated model metadata

        Returns:
            The URI to the directory containing the registered model.
        """
        model_uri = self._get_correct_model_uri(request, metadata)

        if model_uri is None:
            raise RegistrationError("the model_uri does not exist")

        logger.info("ModelRegistrar: registering model: %s", request)
        registry_path = self._copy_model_to_registry(request, model_uri)
        logger.info("ModelRegistrar: registered model: %s path=%s", request, registry_path)
        return registry_path
