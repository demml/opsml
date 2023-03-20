from typing import Union
import tempfile
import zipfile
from io import BytesIO
import os
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Body, Request
from opsml_artifacts.scripts.load_model_card import ModelLoaderCli
from opsml_artifacts import CardRegistry
from opsml_artifacts.app.core.config import config
from opsml_artifacts.app.routes.models import (
    AddRecordRequest,
    AddRecordResponse,
    ListRequest,
    ListResponse,
    StorageSettingsResponse,
    UidExistsRequest,
    UidExistsResponse,
    UpdateRecordRequest,
    UpdateRecordResponse,
    VersionRequest,
    VersionResponse,
    DownloadModelRequest,
)
from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()


@router.get("/settings", response_model=StorageSettingsResponse, name="settings")
def get_storage_settings() -> StorageSettingsResponse:
    """Returns backend storage path and type"""

    if bool(config.STORAGE_URI):

        # TODO (steven) - Think of a different way to do this in the future
        # do we need to return anything if using proxy for both registration and storage

        if not config.is_proxy:

            if "gs://" in config.STORAGE_URI:
                return StorageSettingsResponse(
                    storage_type="gcs",
                    storage_uri=config.STORAGE_URI,
                )

    return StorageSettingsResponse(
        storage_type="local",
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

    """Sets the version for an artifact card. It also checks if a uid already exists"""
    table_for_registry = payload.table_name.split("_")[1].lower()
    registry: CardRegistry = getattr(request.app.state.registries, table_for_registry)

    dataframe = registry.list_cards(
        uid=payload.uid,
        name=payload.name,
        team=payload.team,
        version=payload.version,
    )

    records = dataframe.to_dict("records")

    return ListResponse(records=records)


@router.post("/create", response_model=AddRecordResponse, name="create")
def add_record(
    request: Request,
    payload: AddRecordRequest = Body(...),
) -> AddRecordResponse:

    """Sets the version for an artifact card. It also checks if a uid already exists"""
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


@router.post("/download", response_model=DownloadModelRequest, name="download")
def download_model(
    request: Request,
    payload: DownloadModelRequest = Body(...),
) -> UpdateRecordResponse:

    """Downloads a model card"""

    zip_subdir = "model_defs"

    registry: CardRegistry = getattr(request.app.state.registries, "model")
    with tempfile.TemporaryDirectory() as tmp_dir:
        loader = ModelLoaderCli(
            base_path=tmp_dir,
            registry=registry,
            **payload.dict(),
        )
        loader.save_to_local_file()

        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
            for path in loader.file_paths:
                path_to_write = path.split(tmp_dir)[1]
                zip_path = os.path.join(zip_subdir, path_to_write)
                temp_zip.write(path, zip_path)

    return StreamingResponse(
        iter([zip_io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=models.zip"},
    )
