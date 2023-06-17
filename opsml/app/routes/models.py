# pylint: disable=protected-access
import os
from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException, Request, status

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
from opsml.registry.storage.storage_system import StorageClientType

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


class ModelRegistrar:
    """Class used to register a model to a hardcoded uri"""

    def __init__(self, payload: CardRequest, storage_client: StorageClientType):
        """Instantiates Registrar class

        Args:
            payload:
                `CardRequest`
            storage_client:
                `StorageClientType`
        """
        self.name = payload.name
        self.team = payload.team
        self.version = payload.version
        self.onnx = payload.onnx
        self.storage_client = storage_client
        self._validate_version()

    @property
    def registry_path(self) -> str:
        """Returns hardcoded uri"""
        return f"{self.storage_client.base_path_prefix}/model_registry/{self.team}/{self.name}/v{self.version}"

    @property
    def registry_not_empty(self) -> bool:
        """Verifies model has been copied to hardcoded path"""
        if len(self.storage_client.list_files(self.registry_path)) > 0:
            return True
        return False

    def _validate_version(self) -> None:
        """Checks whether a version given follows semver/integer format

        Args:
            version:
                Version to check
        """
        try:
            for element in self.version.split("."):
                int(element)  # force check element is an integer

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found. Model semver invalid",
            )

    def _get_correct_model_uri(self, metadata: ModelMetadata) -> str:
        """Gets correct model uri based on onnx flag

        Args:
            onnx:
                Bool indicating if onnx uri is requested
            metadata:
                `ModelMetadata`
        """
        if self.onnx:
            return metadata.onnx_uri
        return metadata.model_uri

    def _copy_model_to_registry(self, model_uri: str):
        """Copies a model from it's original storage path to a hardcoded model registry path

        Args:
            model_uri:
                Model uri path
            storage_client:
                Storage client to use to copy
            name:
                Model name
            team:
                Team name

        Returns:
            New model path

        """
        read_path = os.path.dirname(model_uri)

        self.storage_client.copy(read_path=read_path, write_path=self.registry_path)

        if self.registry_not_empty:
            return self.registry_path

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found in registry path",
        )

    def register_model(self, metadata: ModelMetadata) -> str:
        """Registers a model to a hardcoded storage path

        Args:
            metadata:
                `ModelMetadata`

        Returns:
            model uri

        """
        model_uri = self._get_correct_model_uri(metadata=metadata)

        if model_uri is not None:
            return self._copy_model_to_registry(model_uri=model_uri)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found. Check if model exists in Opsml registry",
        )


@router.post("/models/register", name="register")
def post_register_model(request: Request, payload: CardRequest) -> str:
    """Promotes a model from Opsml storage to the default model registry storage used for
    Seldon model hosting.

    Args:
        name:
            Optional name of model
        version:
            Optional semVar version of model
        team:
            Optional team name
        uid:
            Optional uid of ModelCard
        onnx:
            Whether to copy the onnx model or model in it's native format. Defaults to True

    Returns:
        model uri or HTTP_404_NOT_FOUND if the model is not found.
    """

    # instantiate registrar first (we want to validate version before loading metadata)
    registrar = ModelRegistrar(
        payload=payload,
        storage_client=request.app.state.storage_client,
    )

    # get model metadata
    metadata = post_model_metadata(request, payload)

    # register/copy to new location
    return registrar.register_model(metadata=metadata)


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

    try:
        model_card: ModelCard = registry.load_card(  # type:ignore
            name=payload.name,
            team=payload.team,
            uid=payload.uid,
            version=payload.version,
        )

    except IndexError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        ) from exc

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
