# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from opsml.app.core.config import config
from opsml.app.core.dependencies import verify_token
from opsml.app.routes.pydantic_models import (
    AddCardRequest,
    AddCardResponse,
    DeleteCardRequest,
    DeleteCardResponse,
    ListCardRequest,
    ListCardResponse,
    NamesResponse,
    TeamsResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateCardRequest,
    UpdateCardResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import get_registry_type_from_table, replace_proxy_root
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistry

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.post("/cards/uid", response_model=UidExistsResponse, name="check_uid")
def check_uid(
    request: Request,
    payload: UidExistsRequest = Body(...),
) -> UidExistsResponse:
    """Checks if a uid already exists in the database"""

    registry_type = get_registry_type_from_table(
        table_name=payload.table_name,
        registry_type=payload.registry_type,
    )

    registry: CardRegistry = getattr(request.app.state.registries, registry_type)

    if registry._registry.check_uid(
        uid=payload.uid,
        registry_type=registry.registry_type,
    ):
        return UidExistsResponse(uid_exists=True)
    return UidExistsResponse(uid_exists=False)


@router.get("/cards/teams", response_model=TeamsResponse, name="teams")
def card_teams(
    request: Request,
    registry_type: str,
) -> TeamsResponse:
    """Get all teams associated with a registry

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry

    Returns:
        `TeamsResponse`
    """
    registry: CardRegistry = getattr(request.app.state.registries, registry_type)

    teams = registry._registry.unique_teams

    return TeamsResponse(teams=teams)


@router.get("/cards/names", response_model=NamesResponse, name="names")
def card_names(
    request: Request,
    registry_type: str,
    team: Optional[str] = None,
):
    """Get all names associated with a registry

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry
        team:
            Team to filter names by

    Returns:
        `NamesResponse`
    """

    registry: CardRegistry = getattr(request.app.state.registries, registry_type)
    names = registry._registry.get_unique_card_names(team=team)

    return NamesResponse(names=names)


@router.post(
    "/cards/version",
    response_model=Union[VersionResponse, UidExistsResponse],
    name="version",
)
def set_version(
    request: Request,
    payload: VersionRequest = Body(...),
) -> Union[VersionResponse, UidExistsResponse]:
    """Sets the version for an artifact card"""

    registry_type = get_registry_type_from_table(
        table_name=payload.table_name,
        registry_type=payload.registry_type,
    )

    registry: CardRegistry = getattr(request.app.state.registries, registry_type)

    try:
        version = registry._registry.set_version(
            name=payload.name,
            team=payload.team,
            supplied_version=payload.version,
            version_type=payload.version_type,
            pre_tag=payload.pre_tag,
            build_tag=payload.build_tag,
        )

        return VersionResponse(version=version)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set version. {error}",
        ) from error


@router.post("/cards/list", response_model=ListCardResponse, name="list_cards")
def list_cards(
    request: Request,
    payload: ListCardRequest = Body(...),
) -> ListCardResponse:
    """Lists a Card"""

    try:
        registry_type = get_registry_type_from_table(
            table_name=payload.table_name,
            registry_type=payload.registry_type,
        )

        registry: CardRegistry = getattr(request.app.state.registries, registry_type)
        logger.info("Listing cards with request: {}", payload.model_dump())

        cards = registry.list_cards(
            uid=payload.uid,
            name=payload.name,
            team=payload.team,
            version=payload.version,
            max_date=payload.max_date,
            limit=payload.limit,
            tags=payload.tags,
            as_dataframe=False,
            ignore_release_candidates=payload.ignore_release_candidates,
        )

        if config.is_proxy:
            cards = [
                replace_proxy_root(
                    card=card,
                    storage_root=config.STORAGE_URI,
                    proxy_root=str(config.proxy_root),
                )
                for card in cards
            ]

        return ListCardResponse(cards=cards)

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
def create_card(
    request: Request,
    payload: AddCardRequest = Body(...),
) -> AddCardResponse:
    """Adds Card record to a registry"""

    try:
        registry_type = get_registry_type_from_table(
            table_name=payload.table_name,
            registry_type=payload.registry_type,
        )

        registry: CardRegistry = getattr(request.app.state.registries, registry_type)

        logger.info("Creating card: {}", payload.model_dump())

        registry._registry.add_and_commit(card=payload.card)
        return AddCardResponse(registered=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Error creating card in registry. {error}""",
        ) from error


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

    try:
        registry_type = get_registry_type_from_table(
            table_name=payload.table_name,
            registry_type=payload.registry_type,
        )
        registry: CardRegistry = getattr(request.app.state.registries, registry_type)
        registry._registry.update_card_record(card=payload.card)

        logger.info("Updated card: {}", payload.model_dump())

        return UpdateCardResponse(updated=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Error updating card in registry. {error}""",
        ) from error


@router.post(
    "/cards/delete",
    response_model=DeleteCardResponse,
    name="delete_card",
    dependencies=[Depends(verify_token)],
)
def delete_card(
    request: Request,
    payload: DeleteCardRequest = Body(...),
) -> DeleteCardResponse:
    """Deletes a specific artifact card"""

    try:
        registry_type = get_registry_type_from_table(
            table_name=payload.table_name,
            registry_type=payload.registry_type,
        )
        registry: CardRegistry = getattr(request.app.state.registries, registry_type)
        registry._registry.delete_card_record(card=payload.card)
        logger.info("Deleted card: {}", payload.model_dump())

        return DeleteCardResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Error deleting card record from registry. {error}""",
        ) from error
