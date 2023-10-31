# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from fastapi import APIRouter, Request


from opsml.app.routes.pydantic_models import TableNameResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.sql_schema import RegistryTableNames

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

    return TableNameResponse(table_name=RegistryTableNames[registry_type.upper()].value)
