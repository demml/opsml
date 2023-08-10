# License: MIT

from fastapi import HTTPException, Request

from opsml.app.core.config import config
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


def verify_token(request: Request):
    """Verifies production token if APP_ENV is production"""
    prod_token = request.headers.get("X-Prod-Token")

    if config.APP_ENV == "production":
        if prod_token != config.PROD_TOKEN:
            logger.error("Attempt to write prod without token")
            raise HTTPException(
                status_code=400,
                detail="Cannot perform write operation on prod resource without token",
            )
