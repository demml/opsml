# pylint: disable=protected-access
from typing import Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from opsml.app.core.config import config
from opsml.app.core.dependencies import verify_token
from opsml.app.routes.pydantic_models import (
    AddCardRequest,
    AddCardResponse,
    ListRequest,
    ListResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateCardRequest,
    UpdateCardResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import replace_proxy_root
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistry

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()


@router.post("/cards/uid", response_model=UidExistsResponse, name="check_uid")
def check_uid(
    request: Request,
    payload: UidExistsRequest = Body(...),
) -> UidExistsResponse:
    """Checks if a uid already exists in the database"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    if registry._registry.check_uid(
        uid=payload.uid,
        table_to_check=payload.table_name,
    ):
        return UidExistsResponse(uid_exists=True)
    return UidExistsResponse(uid_exists=False)


@router.post("/cards/version", response_model=Union[VersionResponse, UidExistsResponse], name="version")
def set_version(
    request: Request,
    payload: VersionRequest = Body(...),
) -> Union[VersionResponse, UidExistsResponse]:
    """Sets the version for an artifact card"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    version = registry._registry.set_version(
        name=payload.name,
        team=payload.team,
        version_type=payload.version_type,
    )

    return VersionResponse(version=version)


@router.post("/cards/list", response_model=ListResponse, name="list_cards")
def list_cards(
    request: Request,
    payload: ListRequest = Body(...),
) -> ListResponse:
    """Lists a Card"""

    try:
        table_for_registry = payload.table_name.split("_")[1].lower()
        registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

        cards = registry.list_cards(
            uid=payload.uid,
            name=payload.name,
            team=payload.team,
            version=payload.version,
            max_date=payload.max_date,
            limit=payload.limit,
            tags=payload.tags,
            as_dataframe=False,
        )

        if config.is_proxy:
            cards = [
                replace_proxy_root(
                    card=card,
                    storage_root=config.STORAGE_URI,
                    proxy_root=config.proxy_root,
                )
                for card in cards
            ]

        return ListResponse(cards=cards)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Error listing cards. {error}""",
        ) from error


@router.post(
    "/cards/create",
    response_model=AddCardResponse,
    name="create_card",
    dependencies=[Depends(verify_token)],
)
def add_card(
    request: Request,
    payload: AddCardRequest = Body(...),
) -> AddCardResponse:
    """Adds Card record to a registry"""

    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry._registry.add_and_commit(card=payload.card)
    return AddCardResponse(registered=True)


@router.post(
    "/cards/update",
    response_model=UpdateCardResponse,
    name="update_card",
    dependencies=[Depends(verify_token)],
)
def update_card(
    request: Request,
    payload: UpdateCardRequest = Body(...),
) -> UpdateCardResponse:
    """Updates a specific artifact card"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry._registry.update_card_record(card=payload.card)

    return UpdateCardResponse(updated=True)
