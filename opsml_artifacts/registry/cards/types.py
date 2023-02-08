from enum import Enum
from typing import Any

from pydantic import BaseModel


class StoragePath(BaseModel):
    uri: str


class SaveInfo(BaseModel):
    blob_path: str
    name: str
    version: int
    team: str

    class Config:
        allow_mutation = True


class StorageClientInfo(BaseModel):
    storage_folder: str = "opsml_storage"
    storage_client: Any


class ArtifactStorageTypes(str, Enum):
    DATAFRAME = "DataFrame"
    ARROW_TABLE = "Table"
    NDARRAY = "ndarray"
    TF_MODEL = "keras"
    PYTORCH = "pytorch"


class CardNames(str, Enum):
    DATA = "data"
    EXPERIMENT = "experiment"
    MODEL = "model"
    PIPELINE = "pipeline"


NON_PIPELINE_CARDS = [card.value for card in CardNames if card.value != "pipeline"]


DATA_ARTIFACTS = list(ArtifactStorageTypes)
