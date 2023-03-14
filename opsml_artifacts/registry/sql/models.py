from typing import Any, Optional, Dict, Union

from pydantic import BaseModel


class SaveInfo(BaseModel):
    blob_path: str
    name: str
    version: str
    team: str
    filename: Optional[str] = None
    storage_client: Any
    extra: Dict[str, Any] = {}

    class Config:
        allow_mutation = True
