# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access


from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import (
    DriftProfileRequest,
    DriftResponse,
    GetDriftProfileResponse,
    Success,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.storage.scouter import ScouterClient

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.post("/drift/profile", name="insert_drift_profile", response_model=Success)
def insert_profile(request: Request, payload: DriftProfileRequest) -> Success:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        payload:
            DriftProfileRequest

    Returns:
        200
    """

    client: ScouterClient = request.app.state.scouter_client

    try:
        client.insert_drift_profile(payload.profile)
        return Success()
    except Exception as error:
        logger.error(f"Failed to insert drift profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert drift profile"
        ) from error


@router.get("/drift/profile", name="get_profile", response_model=GetDriftProfileResponse)
def get_profile(
    request: Request,
    repository: str,
    name: str,
    version: str,
) -> GetDriftProfileResponse:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        repository:
            Model repository
        name:
            Model name
        version:
            Model version

    Returns:
        DriftProfile string
    """

    client: ScouterClient = request.app.state.scouter_client

    try:
        profile = client.get_drift_profile(repository, name, version)
        return GetDriftProfileResponse(profile=profile)
    except Exception as error:
        logger.error(f"Failed to get drift profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get drift profile"
        ) from error


@router.get("/drift/values", name="get_drift", response_model=DriftResponse)
def get_drift_values(
    request: Request,
    repository: str,
    name: str,
    version: str,
    time_window: str,
    max_data_points: int,
) -> DriftResponse:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        repository:
            Model repository
        name:
            Model name
        version:
            Model version
        time_window:
            Time window
        max_data_points:
            Maximum data points

    Returns:
        DriftProfile string
    """

    client: ScouterClient = request.app.state.scouter_client

    try:
        values = client.get_drift_values(
            repository,
            name,
            version,
            time_window,
            max_data_points,
        )

        return DriftResponse(**values)
    except Exception as error:
        logger.error(f"Failed to get drift values: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get drift values"
        ) from error
