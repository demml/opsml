from contextlib import contextmanager
from enum import Enum
from typing import Any, Generator, List, Optional, Protocol, Tuple

from pydantic import BaseModel

from opsml_artifacts.registry.sql.models import ArtifactStorageInfo


class StoragePath(BaseModel):
    uri: str


class ArtifactStorageTypes(str, Enum):
    DATAFRAME = "DataFrame"
    ARROW_TABLE = "Table"
    NDARRAY = "ndarray"
    TF_MODEL = "keras"
    PYTORCH = "pytorch"
    JSON = "json"


class CardNames(str, Enum):
    DATA = "data"
    EXPERIMENT = "experiment"
    MODEL = "model"
    PIPELINE = "pipeline"


NON_PIPELINE_CARDS = [card.value for card in CardNames if card.value != "pipeline"]


DATA_ARTIFACTS = list(ArtifactStorageTypes)


class StorageClientProto(Protocol):
    backend: str
    client: Any
    base_path_prefix: str

    def create_save_path(
        self,
        artifact_storage_info: ArtifactStorageInfo,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:
        "Creates a save path"

    def create_tmp_path(
        self,
        artifact_storage_info: ArtifactStorageInfo,
        tmp_dir: str,
        file_suffix: Optional[str] = None,
    ):
        """Temp path"""

    @contextmanager
    def create_temp_save_path(
        self,
        artifact_storage_info: ArtifactStorageInfo,
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


class RegistryRecordProto:
    def dict(self):
        """Create dict from pydantic model"""


class ArtifactCardProto(Protocol):
    name: str
    team: str
    uid: str

    def create_registry_record(self, uid: str, version: str) -> RegistryRecordProto:
        """Create registry record"""
