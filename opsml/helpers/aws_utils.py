import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class AwsCredsSetter(BaseModel):
    secret: Optional[str] = None
    access_key: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model_args["access_key"] = os.getenv("AWS_ACCESS_KEY_ID")
        model_args["secret"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        model_args["token"] = os.getenv("AWS_SESSION_TOKEN")

        return model_args
