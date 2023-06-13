# pylint: disable=protected-access
from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import Response

from opsml.app.routes.pydantic_models import (
    CardRequest,
    CompareMetricRequest,
    CompareMetricResponse,
    MetricRequest,
    MetricResponse,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.model.challenger import ModelChallenger
from opsml.registry import CardInfo, CardRegistries, CardRegistry, ModelCard, RunCard
from opsml.registry.cards.cards import ModelMetadata

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


@router.post("/models/uri", name="model_uri")
def post_model_uri(request: Request, payload: CardRequest) -> str:
    """Retrieves the onnx model URI"""
    return post_model_metadata(request, payload).onnx_uri


@router.post("/models/metadata", name="model_metadata")
def post_model_metadata(request: Request, payload: CardRequest) -> ModelMetadata:
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
        ModelMetadata or HTTP_404_NOT_FOUND if the model is not found.
    """
    registry: CardRegistry = request.app.state.registries.model

    # load model card
    model_card: ModelCard = None
    try:
        # BUG: Requesting ^1.0.1 will return 1.0.0
        model_card: ModelCard = registry.load_card(
            name=payload.name,
            team=payload.team,
            uid=payload.uid,
            version=payload.version,
        )
    except IndexError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    assert isinstance(model_card.card_type, ModelCard)
    return model_card.model_metadata


@router.post("/models/metrics", response_model=MetricResponse, name="model_metrics")
def post_model_metrics(
    request: Request,
    payload: MetricRequest = Body(...),
) -> MetricResponse:
    """Gets metrics associated with a ModelCard"""

    # Get model runcard id
    registries: CardRegistries = request.app.state.registries
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
            detail="More than one card found",
        )

    card = cards[0]
    if card.get("runcard_uid") is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model is not associated with a run",
        )

    runcard: RunCard = registries.run.load_card(uid=card.get("runcard_uid"))

    return MetricResponse(metrics=runcard.metrics)


@router.post("/models/compare_metrics", response_model=CompareMetricResponse, name="compare_model_metrics")
def compare_metrics(
    request: Request,
    payload: CompareMetricRequest = Body(...),
) -> CompareMetricResponse:
    """Compare model metrics using `ModelChallenger`"""

    try:
        # Get challenger
        registries: CardRegistries = request.app.state.registries
        challenger_card: ModelCard = registries.model.load_card(uid=payload.challenger_uid)

        model_challenger = ModelChallenger(challenger=challenger_card)

        champions = [CardInfo(uid=champion_uid) for champion_uid in payload.champion_uid]
        battle_report = model_challenger.challenge_champion(
            metric_name=payload.metric_name,
            champions=champions,
            lower_is_better=payload.lower_is_better,
        )

        return CompareMetricResponse(
            challenger_name=challenger_card.name,
            challenger_version=challenger_card.version,
            report=battle_report,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare model metrics. {error}",
        ) from error
