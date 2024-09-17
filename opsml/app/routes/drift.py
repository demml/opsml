# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import DriftProfileRequest, Success
from opsml.helpers.logging import ArtifactLogger
from opsml.storage.scouter import ScouterClient
from typing import cast

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert drift profile") from error


@router.get("/drift/profile", name="get_profile", response_model=str)
def get_profile(
    request: Request,
    repository: str,
    name: str,
    version: str,
) -> str:
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
        response = client.get_drift_profile(repository, name, version)

        print(response)
        profile = response.get("data")

        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drift profile not found")

        return cast(str, profile)
    except Exception as error:
        logger.error(f"Failed to get drift profile: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get drift profile") from error
