# pylint: disable=protected-access
import os
from typing import Any, Dict, List, Union

import streaming_form_data
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml.app.core.config import config
from opsml.app.routes.models import (
    AddCardRequest,
    AddCardResponse,
    DownloadFileRequest,
    DownloadModelRequest,
    ListFileRequest,
    ListFileResponse,
    ListRequest,
    ListResponse,
    StorageSettingsResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateCardRequest,
    UpdateCardResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import (
    MODEL_METADATA_FILE,
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
    replace_proxy_root,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistry
from opsml.registry.storage.storage_system import StorageSystem

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 50  # = 50GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024


@router.get("/settings", response_model=StorageSettingsResponse, name="settings")
def get_storage_settings() -> StorageSettingsResponse:
    """Returns backend storage path and type"""

    if bool(config.STORAGE_URI):
        if not config.is_proxy:
            if "gs://" in config.STORAGE_URI:
                return StorageSettingsResponse(
                    storage_type=StorageSystem.GCS.value,
                    storage_uri=config.STORAGE_URI,
                )

        # this should setup the api storage client
        if config.is_proxy:
            return StorageSettingsResponse(
                storage_type=StorageSystem.API.value,
                storage_uri=config.STORAGE_URI,
                proxy=config.is_proxy,
            )

    return StorageSettingsResponse(
        storage_type=StorageSystem.LOCAL.value,
        storage_uri=config.STORAGE_URI,
        proxy=config.is_proxy,
    )


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
            limit=payload.limit,
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


@router.post("/cards/create", response_model=AddCardResponse, name="create_card")
def add_card(
    request: Request,
    payload: AddCardRequest = Body(...),
) -> AddCardResponse:
    """Adds Card record to a registry"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry._registry.add_and_commit(card=payload.card)
    return AddCardResponse(registered=True)


@router.post("/cards/update", response_model=UpdateCardResponse, name="update_card")
def update_card(
    request: Request,
    payload: UpdateCardRequest = Body(...),
) -> UpdateCardResponse:
    """Updates a specific artifact card"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry._registry.update_card_record(card=payload.card)

    return UpdateCardResponse(updated=True)


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


# upload uses the request object directly which affects OpenAPI docs
@router.post("/upload", name="upload")
async def upload_file(request: Request):
    """Uploads files in chunks to storage destination"""

    filename = request.headers.get("Filename")
    write_path = request.headers.get("WritePath")
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename header is missing",
        )

    if write_path is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No write path provided",
        )

    try:
        file_ = ExternalFileTarget(
            filename=filename,
            write_path=write_path,
            storage_client=request.app.state.storage_client,
            validator=MaxSizeValidator(MAX_FILE_SIZE),
        )
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register("file", file_)

        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)

    except ClientDisconnect:
        logger.error("Client disconnected")

    except MaxBodySizeException as error:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"""
               Maximum request body size limit ({MAX_REQUEST_BODY_SIZE}.
               Bytes exceeded ({error.body_len} bytes read)""",
        ) from error

    except streaming_form_data.validators.ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error uploading the file. {error}",
        ) from error

    if not file_.multipart_filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is missing",
        )
    return {
        "storage_uri": os.path.join(write_path, filename),
    }


@router.post("/files/download", name="download_file")
def download_file(
    request: Request,
    payload: DownloadFileRequest,
) -> StreamingResponse:
    """Downloads a file

    Args:
        read_path (str):
            Path to read from

    Returns:
        Streaming file response
    """

    try:
        storage_client = request.app.state.storage_client
        return StreamingResponse(
            storage_client.iterfile(
                file_path=payload.read_path,
                chunk_size=CHUNK_SIZE,
            ),
            media_type="application/octet-stream",
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


@router.post("/files/list", name="list_files")
def list_files(
    request: Request,
    payload: ListFileRequest,
) -> ListFileResponse:
    """Downloads a file

    Args:
        read_path (str):
            Path to search

    Returns:
        List of files
    """

    try:
        storage_client = request.app.state.storage_client
        files = storage_client.list_files(payload.read_path)
        return ListFileResponse(files=files)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error
