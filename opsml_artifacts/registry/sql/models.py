from typing import Any, Optional

from pydantic import BaseModel


class SaveInfo(BaseModel):
    blob_path: str
    name: str
    version: str
    team: str
    filename: Optional[str] = None
    storage_client: Any

    class Config:
        allow_mutation = True
