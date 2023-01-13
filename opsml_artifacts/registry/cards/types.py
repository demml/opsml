from enum import Enum
from pydantic import BaseModel
import numpy as np
import pandas as pd


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


DATA_ARTIFACTS = [
    ArtifactStorageTypes.DATAFRAME,
    ArtifactStorageTypes.ARROW_TABLE,
    ArtifactStorageTypes.NDARRAY,
]


class Base(BaseModel):
    def to_onnx(self):
        raise NotImplementedError

    def to_dataframe(self):
        raise NotImplementedError


class NumpyBase(Base):
    def to_onnx(self):
        return {
            "inputs": np.array(
                [list(self.dict().values())],
                np.float32,
            ).reshape(1, -1)
        }

    def to_dataframe(self):
        raise NotImplementedError


class PandasBase(Base):
    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            if isinstance(feat_val, float):
                feats[feat] = np.array([[feat_val]]).astype(np.float32)
            elif isinstance(feat_val, int):
                feats[feat] = np.array([[feat_val]]).astype(np.int64)
            else:
                feats[feat] = np.array([[feat_val]])
        return feats

    def to_dataframe(self):
        return pd.DataFrame(self.dict(), index=[0])
