# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import DriftProfileRequest, Success
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerModelCardRegistry

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.post("/drift/profile", name="metric_put", response_model=Success)
def insert_metric(request: Request, payload: DriftProfileRequest) -> Success:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        payload:
            DriftProfileRequest

    Returns:
        200
    """

    model_reg: ServerModelCardRegistry = request.app.state.registries.model._registry

    try:
        model_reg.insert_drift_profile(payload.profile)
        return Success()
    except Exception as error:
        logger.error(f"Failed to insert metrics: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert drift profile"
        ) from error
