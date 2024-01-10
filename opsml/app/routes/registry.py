# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import TableNameResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.types import RegistryTableNames

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.get("/registry/table", response_model=TableNameResponse, name="table_name")
def get_table_name(request: Request, registry_type: str) -> TableNameResponse:
    """Gets table name for a given registry type

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry

    Returns:
        `TableNameResponse`
    """

    try:
        table_name = RegistryTableNames[registry_type.upper()].value
        return TableNameResponse(table_name=table_name)

    except KeyError as exc:
        logger.error(f"Registry type {registry_type} does not exist")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Registry type {registry_type} does not exist""",
        ) from exc
