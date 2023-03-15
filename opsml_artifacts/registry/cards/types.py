from enum import Enum
from typing import Protocol
from pydantic import BaseModel


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


class RegistryRecordProto:
    def dict(self):
        """Create dict from pydantic model"""


class ArtifactCardProto(Protocol):
    name: str
    team: str
    uid: str

    def create_registry_record(self) -> RegistryRecordProto:
        """Create registry record"""
