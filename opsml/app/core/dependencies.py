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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot perform write operation on prod resource without token",
            )


def _verify_path(path: Path) -> None:
    """Verifies path contains one of our card table names.

    All files being read from or written to opsml should be written to one of
    our known good card directories - which are the same as our SQL table names.

    Args:
        path: path to verify

    Raises:
        HTTPException: Invalid path
    """
    # all artifacts belong to a registry
    if any(table_name in path.as_posix() for table_name in RegistryTableNames):
        return

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Path is not a valid registry path",
    )


def swap_opsml_root(request: Request, path: Path) -> Path:
    """When running in client model, client will specify path to use with opsml_proxy_root.
    Server needs to swap this out with opsml_storage_uri to access the correct path.

    Args:
        request:
            Request object
        path:
            path to swap

    Returns:
        new path
    """

    _verify_path(path)

    if path.as_posix().startswith(config.opsml_proxy_root):
        curr_path = path
        new_path = Path(request.app.state.storage_root) / curr_path.relative_to(config.opsml_proxy_root)
        return new_path
    return path


def reverse_swap_opsml_root(request: Request, path: Path) -> Path:
    """When running in client model, client will specify path to use with opsml_proxy_root.
    Server needs to swap this out with opsml_storage_uri to access the correct path.

    Args:
        request:
            Request object
        path:
            path to swap

    Returns:
        new path
    """

    _verify_path(path)

    if not path.as_posix().startswith(config.opsml_proxy_root):
        curr_path = path
        new_path = Path(config.opsml_proxy_root) / curr_path.relative_to(request.app.state.storage_root)
        return new_path
    return path
