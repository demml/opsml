from enum import Enum

from pydantic import BaseModel


class StoragePath(BaseModel):
    gcs_uri: str


class SaveInfo(BaseModel):
    blob_path: str
    name: str
    version: int
    team: str


class ArtifactStorageTypes(str, Enum):
    DATAFRAME = "DataFrame"
    ARROW_TABLE = "Table"
    NDARRAY = "ndarray"


class CardNames(str, Enum):
    DATA = "data"
    EXPERIMENT = "experiment"
    MODEL = "model"
    PIPELINE = "pipeline"


NON_PIPELINE_CARDS = [card.value for card in CardNames if card.value != "pipeline"]


DATA_ARTIFACTS = list(ArtifactStorageTypes)
