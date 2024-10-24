# pylint: disable=protected-access
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Dict, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from opsml.app.core.dependencies import verify_token
from opsml.app.routes.pydantic_models import (
    AddCardRequest,
    AddCardResponse,
    DeleteCardRequest,
    DeleteCardResponse,
    ListCardRequest,
    ListCardResponse,
    RegistryQuery,
    RepositoriesResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateCardRequest,
    UpdateCardResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import get_registry_type_from_table
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


@router.get("/cards/repositories", response_model=RepositoriesResponse, name="repositories")
def card_repositories(
    request: Request,
    registry_type: str,
) -> RepositoriesResponse:
    """Get all repositories associated with a registry

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry

    Returns:
        `RepositoriesResponse`
    """
    registry: CardRegistry = getattr(request.app.state.registries, registry_type)

    repositories = registry._registry.unique_repositories

    return RepositoriesResponse(repositories=repositories)


@router.get("/cards/registry/stats", name="registry_stats")
def query_registry_stats(
    request: Request,
    registry_type: str,
    search_term: Optional[str] = None,
) -> Dict[str, int]:
    """Get card information from a registry

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry
        search_term:
            search term to filter by. This term can be a repository or a name

    Returns:
        `dict`
    """

    try:
        registry: CardRegistry = getattr(request.app.state.registries, registry_type)
        stats: Dict[str, int] = registry._registry.query_stats(search_term)

        return stats

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query registry. {error}",
        ) from error


@router.get("/cards/registry/query/page", response_model=RegistryQuery, name="registry_page")
def query_registry_page(
    request: Request,
    registry_type: str,
    sort_by: str = "updated_at",
    repository: Optional[str] = None,
    search_term: Optional[str] = None,
    page: int = 0,
) -> RegistryQuery:
    """Get card information from a registry

    Args:
        request:
            FastAPI request object
        registry_type:
            Type of registry
        sort_by:
            Field to sort by
        repository:
            repository to filter by
        search_term:
            search term to filter by. This term can be a repository or a name
        page:
            page number

    Returns:
        `dict`
    """

    try:
        registry: CardRegistry = getattr(request.app.state.registries, registry_type)
        page = registry._registry.query_page(sort_by, page, repository, search_term)
        return RegistryQuery(page=page)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query registry. {error}",
        ) from error


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

    registry: CardRegistry = getattr(request.app.state.registries, payload.registry_type)

    try:
        version = registry._registry.set_version(
            name=payload.name,
            repository=payload.repository,
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
        registry: CardRegistry = getattr(request.app.state.registries, payload.registry_type)

        logger.info("Listing cards with request: {}", payload.model_dump())

        cards = registry._registry.list_cards(
            uid=payload.uid,
            name=payload.name,
            repository=payload.repository,
            version=payload.version,
            max_date=payload.max_date,
            limit=payload.limit,
            tags=payload.tags,
            ignore_release_candidates=payload.ignore_release_candidates,
            query_terms=payload.query_terms,
            sort_by_timestamp=payload.sort_by_timestamp,
        )

        if payload.page:
            cards = cards[payload.page * 30 : payload.page + 30]

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

        # check that deletion was successful
        uid_exists = check_uid(
            request=request,
            payload=UidExistsRequest(
                uid=payload.card.get("uid"),
                table_name=payload.table_name,
                registry_type=payload.registry_type,
            ),
        ).uid_exists

        if uid_exists:
            return DeleteCardResponse(deleted=False)

        logger.info("Deleted card: {}", payload.model_dump())

        return DeleteCardResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""Error deleting card record from registry. {error}""",
        ) from error
