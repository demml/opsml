import os
from typing import Union

import streaming_form_data
from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml.app.core.config import config
from opsml.app.routes.models import (
    AddRecordRequest,
    AddRecordResponse,
    DownloadFileRequest,
    DownloadModelRequest,
    ListFileRequest,
    ListFileResponse,
    ListRequest,
    ListResponse,
    StorageSettingsResponse,
    StorageUri,
    UidExistsRequest,
    UidExistsResponse,
    UpdateRecordRequest,
    UpdateRecordResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import (
    MODEL_FILE,
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
    ModelDownloader,
    delete_dir,
    iterfile,
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


@router.post("/check_uid", response_model=UidExistsResponse, name="check_uid")
def check_uid(
    request: Request,
    payload: UidExistsRequest = Body(...),
) -> UidExistsResponse:

    """Checks if a uid already exists in the database"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    if registry.registry.check_uid(
        uid=payload.uid,
        table_to_check=payload.table_name,
    ):
        return UidExistsResponse(uid_exists=True)
    return UidExistsResponse(uid_exists=False)


@router.post("/version", response_model=Union[VersionResponse, UidExistsResponse], name="version")
def set_version(
    request: Request,
    payload: VersionRequest = Body(...),
) -> Union[VersionResponse, UidExistsResponse]:

    """Sets the version for an artifact card"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    version = registry.registry.set_version(
        name=payload.name,
        team=payload.team,
        version_type=payload.version_type,
    )

    return VersionResponse(version=version)


@router.post("/list", response_model=ListResponse, name="list")
def list_cards(
    request: Request,
    payload: ListRequest = Body(...),
) -> ListResponse:

    """Lists a Card"""

    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    records = registry.registry.list_cards(
        uid=payload.uid,
        name=payload.name,
        team=payload.team,
        version=payload.version,
    )

    if config.is_proxy:

        records = [
            replace_proxy_root(
                record=record,
                storage_root=config.STORAGE_URI,
                proxy_root=config.proxy_root,
            )
            for record in records
        ]

    return ListResponse(records=records)


@router.post("/create", response_model=AddRecordResponse, name="create")
def add_record(
    request: Request,
    payload: AddRecordRequest = Body(...),
) -> AddRecordResponse:

    """Adds Card record to a registry"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry.registry.add_and_commit(record=payload.record)
    return AddRecordResponse(registered=True)


@router.post("/update", response_model=UpdateRecordResponse, name="update")
def update_record(
    request: Request,
    payload: UpdateRecordRequest = Body(...),
) -> UpdateRecordResponse:

    """Updates a specific artifact card"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    registry.registry.update_record(record=payload.record)

    return UpdateRecordResponse(updated=True)


@router.post("/download_model", name="download_model")
def download_model(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: DownloadModelRequest,
) -> StreamingResponse:

    """Downloads a Model API definition

    Args:
        name (str): Optional name of model
        version (str): Optional semVar version of model
        team (str): Optional team name
        uid (str): Optional uid of ModelCard

    Returns:
        FileResponse object containing model definition json
    """

    registry: CardRegistry = getattr(request.app.state.registries, "model")

    loader = ModelDownloader(
        registry=registry,
        model_info=payload,
        config=config,
    )
    loader.download_model()
    background_tasks.add_task(delete_dir, dir_path=loader.base_path)

    headers = {"Content-Disposition": f'attachment; filename="{MODEL_FILE}"'}
    return StreamingResponse(
        iterfile(
            file_path=loader.file_path,
            chunk_size=CHUNK_SIZE,
        ),
        media_type="application/octet-stream",
        headers=headers,
    )


# flush this out next pr (need upload and download path)
@router.post("/upload", name="upload")
async def upload_file(
    request: Request,
    response_model=StorageUri,
):
    """Uploads files in chunks to storage destination"""

    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get("Filename")
    write_path = request.headers.get("WritePath")

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename header is missing",
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

    except MaxBodySizeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"""
               Maximum request body size limit ({MAX_REQUEST_BODY_SIZE}.
               Bytes exceeded ({e.body_len} bytes read)""",
        )
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded",
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error uploading the file. {error}",
        )

    if not file_.multipart_filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is missing",
        )
    return StorageUri(
        storage_uri=os.path.join(write_path, filename),
    )


# eventually combine download_file and download_model


@router.post("/download_file", name="download_file")
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
            detail=f"There was an error uploading the file. {error}",
        )


@router.post("/list_files", name="list_files")
def list_files(
    request: Request,
    payload: ListFileRequest,
) -> StreamingResponse:

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
            detail=f"There was an error uploading the file. {error}",
        )
