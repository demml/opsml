from typing import Annotated
from fastapi import Header, HTTPException

from opsml.app.core.config import config
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


def verify_token(x_token: Annotated[str, Header()]):
    logger.info(x_token)
    if config.APP_ENV == "production":
        if x_token != config.PROD_TOKEN:
            raise HTTPException(
                status_code=400,
                detail="Cannot perform write operation on Prod from non-prod",
            )
