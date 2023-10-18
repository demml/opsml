# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi import HTTPException, Request

from opsml.app.core.config import config
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


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
