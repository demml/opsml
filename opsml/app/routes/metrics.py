# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, HTTPException, Request

from opsml.app.routes.pydantic_models import MetricsModel, MetricUploadResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerRunCardRegistry

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.post("/metrics/upload", response_model=MetricUploadResponse, name="metric_upload")
def insert_metric(request: Request, payload: MetricsModel) -> MetricUploadResponse:
    """Inserts metrics into metric table

    Args:
        request:
            FastAPI request object
        payload:
            MetricsUploadRequest

    Returns:
        `MetricUploadResponse`
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry

    metrics = cast(List[Dict[str, Any]], payload.model_dump()["metric"])
    try:
        run_reg.insert_metric(metrics)
        return MetricUploadResponse(uploaded=True)
    except Exception as error:
        logger.error(f"Failed to insert metrics: {error}")
        raise HTTPException(status_code=400, detail="Failed to insert metrics") from error


@router.post("/metrics/download", response_model=MetricsModel, name="metric_download")
def get_metric(request: Request, run_uid: str, name: Optional[str] = None) -> MetricsModel:
    """Get metrics from metric table

    Args:
        request:
            FastAPI request object
        run_uid:
            Run uid
        name:
            Name of metric

    Returns:
        `MetricUploadResponse`
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry

    try:
        metrics = run_reg.get_metric(run_uid, name)
        return MetricsModel(metric=metrics)

    except Exception as error:
        logger.error(f"Failed to insert metrics: {error}")
        raise HTTPException(status_code=400, detail="Failed to insert metrics") from error
