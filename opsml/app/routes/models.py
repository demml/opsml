# pylint: disable=protected-access
import os
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Request, status, Body
from fastapi.responses import StreamingResponse

from opsml.app.core.config import config
from opsml.app.routes.pydantic_models import DownloadModelRequest, MetricRequest, MetricResponse
from opsml.app.routes.utils import (
    MODEL_METADATA_FILE,
    replace_proxy_root,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistry, CardRegistries, ModelCard, RunCard

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


registries = CardRegistries()


@router.post("/models/metadata", name="download_model_metadata")
def download_model_metadata(request: Request, payload: DownloadModelRequest) -> StreamingResponse:
    """
    Downloads a Model API definition

    Args:
        name:
            Optional name of model
        version:
            Optional semVar version of model
        team:
            Optional team name
        uid:
            Optional uid of ModelCard

    Returns:
        FileResponse object containing model definition json
    """

    registry: CardRegistry = getattr(request.app.state.registries, "model")
    storage_client = request.app.state.storage_client

    cards: List[Dict[str, Any]] = registry.list_cards(
        name=payload.name,
        team=payload.team,
        version=payload.version,
        uid=payload.uid,
        as_dataframe=False,
    )

    if len(cards) > 1:
        logger.warning("More than one model found. Returning latest")

    if not bool(cards):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No model found",
        )

    # swap mlflow proxy root if needed
    if config.is_proxy:
        card = replace_proxy_root(
            card=cards[0],
            storage_root=config.STORAGE_URI,
            proxy_root=config.proxy_root,
        )

    headers = {"Content-Disposition": f'attachment; filename="{MODEL_METADATA_FILE}"'}
    meta_data_uri = card.get("model_metadata_uri")

    try:
        return StreamingResponse(
            storage_client.iterfile(
                file_path=meta_data_uri,
                chunk_size=CHUNK_SIZE,
            ),
            headers=headers,
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading model. {error}",
        ) from error


@router.post("/models/metrics", response_model=MetricResponse, name="model_metrics")
def get_metrics(
    request: Request,
    payload: MetricRequest = Body(...),
) -> MetricResponse:
    """Gets metrics associated with a ModelCard"""

    # Get model runcard id
    cards: List[Dict[str, Any]] = registries.model.list_cards(
        uid=payload.uid,
        name=payload.name,
        team=payload.team,
        version=payload.version,
        as_dataframe=False,
    )

    if len(cards) > 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"More than one card found",
        )

    card = cards[0]
    if card.get("runcard_uid") is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model is not associated with a run",
        )

    runcard: RunCard = registries.run.load_card(uid=card.get("runcard_uid"))

    return MetricResponse(metrics=runcard.metrics)
