# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access


from fastapi import APIRouter, Request

from opsml.app.routes.pydantic_models import ProjectIdResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerProjectCardRegistry

logger = ArtifactLogger.get_logger()


router = APIRouter()


@router.get("/projects/id", response_model=ProjectIdResponse, name="project_id")
def project_id(
    request: Request,
    project_name: str,
    repository: str,
) -> ProjectIdResponse:
    """Get the project ID for the given name / repository.

    Args:
        request:
            FastAPI request object
        project_name:
            Name of the project
        repository:
            Name of the repository

    Returns:
        `ProjectIdResponse`
    """

    registry: ServerProjectCardRegistry = request.app.state.registries.project._registry

    return ProjectIdResponse(
        project_id=registry.get_project_id(
            project_name=project_name,
            repository=repository,
        )
    )
