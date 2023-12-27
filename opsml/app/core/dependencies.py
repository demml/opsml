# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path

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


def swap_opsml_root(read_path: str) -> str:
    """When running in client model, client will specify path to use with opsml_proxy_root.
    Server needs to swap this out with opsml_storage_uri to access the correct path.

    Args:
        path:
            path to swap

    Returns:
        new path
    """

    if read_path.startswith(config.opsml_proxy_root):
        curr_path = Path(read_path)
        new_path = Path(config.opsml_storage_uri) / curr_path.relative_to(config.opsml_proxy_root)
        return str(new_path)
    return read_path
