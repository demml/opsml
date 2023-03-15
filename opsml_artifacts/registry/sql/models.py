from typing import Any, Optional, Dict, Union

from pydantic import BaseModel


class ArtifactStorageInfo(BaseModel):
    blob_path: str
    name: str
    version: str
    team: str
    filename: Optional[str] = None
    storage_client: Any

    class Config:
        allow_mutation = True
