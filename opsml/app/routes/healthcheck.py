# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from fastapi import APIRouter, HTTPException

from opsml.app.routes.pydantic_models import DebugResponse, HealthCheckResult
from opsml.settings.config import config

router = APIRouter()


@router.get("/healthcheck", response_model=HealthCheckResult, name="healthcheck")
async def get_healthcheck() -> HealthCheckResult:
    return HealthCheckResult(is_alive=True)


@router.get("/debug", response_model=DebugResponse, name="debug")
async def debug() -> DebugResponse:
    return DebugResponse(
        url=config.opsml_tracking_uri,
        storage=config.opsml_storage_uri,
        app_env=config.app_env,
        app_version=config.app_version,
    )


@router.get(
    "/error",
    description="An endpoint that will return a 500 error for debugging and alert testing",
)
async def get_error() -> None:
    raise HTTPException(status_code=500)
