# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi import HTTPException, Request

from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import config

logger = ArtifactLogger.get_logger()


def verify_token(request: Request) -> None:
    """Verifies production token if APP_ENV is production"""
    prod_token = request.headers.get("X-Prod-Token")

    if config.app_env == "production":
        if prod_token != config.opsml_prod_token:
            logger.error("Attempt to write prod without token")
            raise HTTPException(
                status_code=400,
                detail="Cannot perform write operation on prod resource without token",
            )
