# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import Metrics, Success
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerRunCardRegistry

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.post("/metrics", name="metric_post", response_model=Success)
def insert_metric(request: Request, payload: Metrics) -> Success:
    """Inserts metrics into metric table

    Args:
        request:
            FastAPI request object
        payload:
            MetricsModel

    Returns:
        200
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry

    metrics = cast(List[Dict[str, Any]], payload.model_dump()["metric"])
    try:
        run_reg.insert_metric(metrics)
        return Success()
    except Exception as error:
        logger.error(f"Failed to insert metrics: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert metrics"
        ) from error


@router.get("/metrics", response_model=Metrics, name="metric_get")
def get_metric(request: Request, run_uid: str, name: Optional[str] = None) -> Metrics:
    """Get metrics from metric table

    Args:
        request:
            FastAPI request object
        run_uid:
            Run uid
        name:
            Name of metric

    Returns:
        `MetricsModel`
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry

    try:
        metrics = run_reg.get_metric(run_uid, name)
        return Metrics(metric=metrics)

    except Exception as error:
        logger.error(f"Failed to get metrics: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get metrics"
        ) from error
