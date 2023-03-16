import os
from contextlib import contextmanager
from typing import Any, Generator, List, Optional, Protocol, Tuple, Union

from pydantic import BaseModel

FilePath = Union[List[str], str]


class StorageClientSettings(BaseModel):
    storage_type: str = "local"
    storage_uri: str = os.path.expanduser("~")


class GcsStorageClientSettings(StorageClientSettings):
    credentials: Optional[Any]
    gcp_project: str


StorageSettings = Union[StorageClientSettings, GcsStorageClientSettings]


class ArtifactStorageSpecs(BaseModel):
    save_path: str
    name: str
    version: str
    team: str
    filename: Optional[str] = None

    class Config:
        allow_mutation = True


class StorageClientProto(Protocol):
    backend: str
    client: Any
    base_path_prefix: str
    _storage_spec: Any

    @property
    def storage_spec(self) -> ArtifactStorageSpecs:
        "storage metadata"

    @storage_spec.setter
    def storage_spec(self, artifact_storage_spec):
        "storage metadata"

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:
        "Creates a save path"

    def create_tmp_path(
        self,
        tmp_dir: str,
        file_suffix: Optional[str] = None,
    ):
        """Temp path"""

    @contextmanager
    def create_temp_save_path(
        self,
        file_suffix: Optional[str],
    ) -> Generator[Tuple[Any, Any], None, None]:
        """Context manager temp save path"""

    def list_files(self, storage_uri: str) -> List[str]:
        """List files"""

    def store(self, storage_uri: Union[List[str], str]) -> Any:
        """store"""

    def upload(self, local_path: str, write_path: str, recursive: bool = False, **kwargs) -> None:
        "Upload"

    def post_process(self, storage_uri: str) -> str:
        "post process"

    @staticmethod
    def validate(storage_backend: str) -> bool:
        """Validate"""


class MlFlowClientProto(Protocol):
    def log_artifact(self, run_id: str, local_path: str, artifact_path: str):
        "log artifact"

    def download_artifacts(self, run_id: str, path: str, dst_path: Optional[str] = None) -> str:
        "download artifact"
