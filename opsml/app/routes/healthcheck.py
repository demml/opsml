# License: MIT
from fastapi import APIRouter, HTTPException

from opsml.app.core.config import config
from opsml.app.routes.pydantic_models import DebugResponse, HealthCheckResult

router = APIRouter()


@router.get("/healthcheck", response_model=HealthCheckResult, name="healthcheck")
def get_healthcheck() -> HealthCheckResult:
    return HealthCheckResult(is_alive=True)


@router.get("/debug", response_model=DebugResponse, name="debug")
async def debug() -> DebugResponse:
    return DebugResponse(
        url=config.TRACKING_URI,
        storage=config.STORAGE_URI,
        app_env=config.APP_ENV,
        proxy_root=config.proxy_root,
        is_proxy=config.is_proxy,
    )


@router.get(
    "/error",
    description="An endpoint that will return a 500 error for debugging and alert testing",
)
def get_error() -> None:
    raise HTTPException(status_code=500)
