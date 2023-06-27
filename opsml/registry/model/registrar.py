import os
from typing import Optional

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt

from opsml.helpers.logging import ArtifactLogger
from opsml.model.types import ModelMetadata
from opsml.registry.storage.storage_system import StorageClientType

logger = ArtifactLogger.get_logger(__name__)


class RegistrationError(Exception):
    # TODO(@damon): Better registration error?
    pass


class RegistrationRequest(BaseModel):
    name: str
    version: str
    team: str
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
        return f"{self.storage_client.base_path_prefix}/model_registry/{request.team}/{request.name}/v{request.version}"

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
            if len(files) == 0:
                return False
            if len(files) == 1:
                # check if file is directory path
                if files[0] == path:
                    return False
            return True
        except FileNotFoundError:
            return False

    def _get_correct_model_uri(self, request: RegistrationRequest, metadata: ModelMetadata) -> Optional[str]:
        """Gets correct model uri based on the request's onnx flag.

        Args:
            request: The model regisration request.
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

        # check if path already has contents
        if self.is_registered(request):
            logger.info("Model detected in registry path. Deleting: %s", registry_path)
            # delete files in existing dir
            self.storage_client.delete(read_path=registry_path)
            assert not self.is_registered(request)

        self.storage_client.copy(read_path=read_path, write_path=registry_path)

        if self.is_registered(request):
            logger.info("Model registered to %s", registry_path)
            return registry_path

        raise RegistrationError()

    def register_model(self, request: RegistrationRequest, metadata: ModelMetadata) -> str:
        """Registers a model to a hardcoded storage path

        Args:
            metadata:
                `ModelMetadata`

        Returns:
            model uri

        """
        model_uri = self._get_correct_model_uri(request, metadata)

        if model_uri is not None:
            return self._copy_model_to_registry(request, model_uri)

        raise RegistrationError()
