import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class AzureCreds(BaseModel):
    account_name: Optional[str] = None
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model_args["account_name"] = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        model_args["tenant_id"] = os.getenv("AZURE_STORAGE_TENANT_ID")
        model_args["client_id"] = os.getenv("AZURE_STORAGE_CLIENT_ID")
        model_args["client_secret"] = os.getenv("AZURE_STORAGE_CLIENT_SECRET")

        return model_args
