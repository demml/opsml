from contextlib import contextmanager
from typing import Any, Generator, List, Optional, Protocol, Tuple
from pydantic import BaseModel


class ArtifactStorageMetadata(BaseModel):
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
    _storage_metadata = Optional[ArtifactStorageMetadata]

    @property
    def storage_meta(self) -> ArtifactStorageMetadata:
        "storage metadata"

    @storage_meta.setter
    def storage_meta(self, artifact_storage_metadata):
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

    def store(self, storage_uri: str) -> Any:
        """store"""

    def upload(self, local_path: str, write_path: str, recursive: bool = False, **kwargs) -> None:
        "Upload"

    def post_process(self, storage_uri: str) -> str:
        "post process"

    @staticmethod
    def validate(storage_backend: str) -> bool:
        """Validate"""
