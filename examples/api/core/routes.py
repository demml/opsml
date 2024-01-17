import numpy as np
from core.models import HealthCheckResult, ModelRequest, ModelResponse
from fastapi import APIRouter, Request

from opsml.helpers.logging import ArtifactLogger

logger: ArtifactLogger = ArtifactLogger.get_logger()

router = APIRouter()


@router.get("/healthcheck", response_model=HealthCheckResult)
async def get_healthcheck() -> HealthCheckResult:
    return HealthCheckResult(is_alive=True)


@router.post("/predict", response_model=ModelResponse, name="predict")
async def predict(request: Request, payload: ModelRequest) -> ModelResponse:
    features = np.array(payload.features).reshape(1, -1).astype(np.float32)
    predictions = request.app.state.model.predict(features)

    return ModelResponse(prediction=predictions)
