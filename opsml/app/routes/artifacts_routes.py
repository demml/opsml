from typing import Union

from fastapi import APIRouter, BackgroundTasks, Body, Request
from fastapi.responses import StreamingResponse

from opsml.app.core.config import config
from opsml.app.routes.models import (
    AddRecordRequest,
    AddRecordResponse,
    DownloadModelRequest,
    ListRequest,
    ListResponse,
    StorageSettingsResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateRecordRequest,
    UpdateRecordResponse,
    VersionRequest,
    VersionResponse,
)
from opsml.app.routes.utils import (
    MODEL_FILE,
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

# MAX_FILE_SIZE = 1024 * 1024 * 1024 * 50  # = 50GB
# MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024


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


@router.post("/download", name="download")
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
# @router.post("/upload", name="upload")
# async def upload_file(request: Request):
#
#    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
#    filename = request.headers.get("Filename")
#
#    if not filename:
#        raise HTTPException( ddd
#            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#            detail="Filename header is missing",
#        )
#
#    try:
#        filepath = os.path.join("./", os.path.basename(filename))
#        file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
#        parser = StreamingFormDataParser(headers=request.headers)
#        parser.register("file", file_)
#
#        async for chunk in request.stream():
#            body_validator(chunk)
#            parser.data_received(chunk)
#
#    except ClientDisconnect:
#        logger.error("Client disconnected")
#
#    except MaxBodySizeException as e:
#        raise HTTPException(
#            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#            detail=f"Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes)
# #exceeded ({e.body_len} bytes read)",
#        )
#    except streaming_form_data.validators.ValidationError:
#        raise HTTPException(
#            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#            detail=f"Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded",
#        )
#
#    except Exception:
#        raise HTTPException(
#            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was an error uploading the file"
#        )
#
#    if not file_.multipart_filename:
#        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is missing")
#
#    return {"message": f"Successfuly uploaded {filename}"}
#
