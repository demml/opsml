# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path

from fastapi import HTTPException, Request, status

from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import config
from opsml.types import RegistryTableNames

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


def _verify_path(path: str) -> None:
    """Verifies path contains one of our card table names.

    All files being read from or written to opsml should be written to one of
    our known good card directories - which are the same as our SQL table names.

    Args:
        path: path to verify

    Raises:
        HTTPException: Invalid path
    """
    # all artifacts belong to a registry
    if any(table_name in path for table_name in [*RegistryTableNames, "model_registry"]):
        return

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Path is not a valid registry path",
    )


def swap_opsml_root(path: str) -> str:
    """When running in client model, client will specify path to use with opsml_proxy_root.
    Server needs to swap this out with opsml_storage_uri to access the correct path.

    Args:
        path:
            path to swap

    Returns:
        new path
    """
    _verify_path(path)

    if path.startswith(config.opsml_proxy_root):
        curr_path = Path(path)
        new_path = Path(config.opsml_storage_uri) / curr_path.relative_to(config.opsml_proxy_root)
        return str(new_path)
    return path
