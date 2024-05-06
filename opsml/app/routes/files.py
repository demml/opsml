# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import io
import json
import tempfile
import zipfile as zp
from pathlib import Path
from typing import Any, Dict, List, Optional

import streaming_form_data
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml import CardRegistry
from opsml.app.core.dependencies import (
    reverse_swap_opsml_root,
    swap_opsml_root,
    verify_token,
)
from opsml.app.routes.pydantic_models import (
    DeleteFileResponse,
    FileExistsResponse,
    FileViewResponse,
    ListFileInfoResponse,
    ListFileResponse,
    ReadMeRequest,
)
from opsml.app.routes.utils import (
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
    calculate_file_size,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import config
from opsml.storage.client import StorageClientBase
from opsml.types import RegistryTableNames
from opsml.types.extra import PresignableTypes

logger = ArtifactLogger.get_logger()


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 50  # = 50GB
MAX_VIEWSIZE = 1024 * 1024 * 2  # = 2MB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
PRESIGN_DEFAULT_EXPIRATION = 60
router = APIRouter()


@router.post("/files/upload", name="upload", dependencies=[Depends(verify_token)])
async def upload_file(request: Request) -> Dict[str, str]:  # pragma: no cover
    """Uploads files in chunks to storage destination"""

    write_path = request.headers.get("write_path")

    if write_path is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No write path provided",
        )

    _write_path = Path(swap_opsml_root(request, Path(write_path)))
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)

    try:
        file_ = ExternalFileTarget(
            write_path=_write_path,
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
    return {"storage_uri": _write_path.as_posix()}


@router.get("/files/download", name="download_file")
def download_file(request: Request, path: str) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        path:
            path to file

    Returns:
        Streaming file response
    """
    logger.info("Server: Downloading file {}", path)
    storage_client: StorageClientBase = request.app.state.storage_client
    try:
        return StreamingResponse(
            storage_client.iterfile(
                Path(swap_opsml_root(request, Path(path))),
                config.download_chunk_size,
            ),
            media_type="application/octet-stream",
        )

    except Exception as error:
        logger.error("Server: Error downloading file {}", path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


def download_dir(request: Request, path: Path) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        path:
            str

    Returns:
        Streaming file response
    """
    storage_client: StorageClientBase = request.app.state.storage_client
    path = swap_opsml_root(request, path)
    try:
        logger.info("Server: Creating zip file for {}", path)
        zip_io = io.BytesIO()

        with tempfile.TemporaryDirectory() as tmpdirname:
            with zp.ZipFile(zip_io, mode="w", compression=zp.ZIP_DEFLATED) as temp_zip:
                lpath = Path(tmpdirname)
                zipfile = lpath / "artifacts"
                rpath = Path(path)
                files = storage_client.find(rpath)

                for file_ in files:
                    curr_rpath = Path(file_)
                    curr_lpath = lpath / curr_rpath.relative_to(rpath)
                    logger.info("Server: Downloading {} to {}", curr_rpath, curr_lpath)
                    storage_client.get(curr_rpath, curr_lpath)
                    zip_filepath = zipfile / curr_rpath.relative_to(rpath)
                    temp_zip.write(curr_lpath, zip_filepath)

            logger.info("Server: Sending zip file for {}", path)
            return StreamingResponse(
                storage_client.iterbuffer(zip_io, config.download_chunk_size),
                media_type="application/x-zip-compressed",
            )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


@router.get("/files/download/ui", name="download_artifacts")
def download_artifacts_ui(request: Request, path: str) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        path:
            path to file

    Returns:
        Streaming file response
    """
    if Path(path).suffix == "":
        return download_dir(request, Path(path))
    return download_file(request, path)


@router.get("/files/list", name="list_files")
def list_files(request: Request, path: str) -> ListFileResponse:
    """Lists files

    Args:
        request:
            request object
        path:
            path to read

    Returns:
        `ListFileResponse`
    """

    swapped_path = swap_opsml_root(request, Path(path))
    storage_client: StorageClientBase = request.app.state.storage_client
    files = storage_client.find(Path(swapped_path))

    try:
        return ListFileResponse(files=[str(reverse_swap_opsml_root(request, Path(file_))) for file_ in files])

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error


@router.get("/files/exists", name="file_exists")
def file_exists(request: Request, path: str) -> FileExistsResponse:
    """Checks if path exists

    Args:
        request:
            request object
        path:
            path to files

    Returns:
        FileExistsResponse
    """
    storage_client: StorageClientBase = request.app.state.storage_client
    return FileExistsResponse(
        exists=storage_client.exists(
            Path(
                swap_opsml_root(request, Path(path)),
            )
        ),
    )


@router.get("/files/delete", name="delete_files", dependencies=[Depends(verify_token)])
def delete_files(request: Request, path: str) -> DeleteFileResponse:
    """Deletes a file

    Args:
        request:
            request object
        path:
            path to file

    Returns:
        `DeleteFileResponse`
    """

    storage_client: StorageClientBase = request.app.state.storage_client
    try:
        try:
            storage_client.rm(Path(swap_opsml_root(request, Path(path))))
            return DeleteFileResponse(deleted=True)

        except FileNotFoundError:
            logger.warning(f"File {path} not found. It may have already been deleted")
            return DeleteFileResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error deleting files. {error}",
        ) from error


@router.get("/files/list/info", name="list_files_info")
def list_files_info(request: Request, path: str, subdir: Optional[str] = None) -> ListFileInfoResponse:
    """Lists files
    Args:
        request:
            request object
        path:
            path to read
        subdir:
            subdirectory to read
    Returns:
        `ListFileResponse`
    """
    storage_path = Path(path)

    if subdir:
        storage_path = storage_path / subdir

    swapped_path = swap_opsml_root(request, storage_path)
    storage_client: StorageClientBase = request.app.state.storage_client

    files: List[Dict[str, Any]] = storage_client.ls(swapped_path, True)

    mtimes = []
    for file_ in files:
        # conversion of timestamp is done on client side to take timezone into account
        mtime = file_["mtime"] * 1000
        uri = Path(file_["name"])
        file_["uri"] = str(reverse_swap_opsml_root(request, uri))
        file_["name"] = uri.name
        file_["size"] = calculate_file_size(file_["size"])
        file_["mtime"] = mtime
        mtimes.append(mtime)

    try:
        return ListFileInfoResponse(
            files=files,
            mtime=max(mtimes),
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error


@router.get("/files/view", name="presign_uri")
def get_file_to_view(request: Request, path: str) -> FileViewResponse:
    """Downloads a file
    Args:
        request:
            request object
        path:
            path to file
    Returns:
        Streaming file response
    """

    swapped_path = swap_opsml_root(request, Path(path))
    storage_client: StorageClientBase = request.app.state.storage_client
    storage_root: str = request.app.state.storage_root
    view_meta: Dict[str, str] = {}
    try:
        file_info = storage_client.client.info(path=swapped_path)
        size = file_info["size"]
        file_info["size"] = calculate_file_size(size)
        file_info["name"] = swapped_path.name
        file_info["mtime"] = file_info["mtime"] * 1000
        file_info["uri"] = path
        file_info["suffix"] = swapped_path.suffix

        if swapped_path.suffix in list(PresignableTypes):
            if size < MAX_VIEWSIZE and swapped_path.suffix in [".txt", ".log", ".json", ".csv", ".py", ".md"]:
                # download load file to string
                with tempfile.TemporaryDirectory() as tmpdirname:
                    lpath = Path(tmpdirname) / swapped_path.name
                    storage_client.get(swapped_path, lpath)

                    with lpath.open("rb") as file_:
                        file_ = file_.read().decode("utf-8")

                        if swapped_path.suffix == ".json":
                            view_meta["content"] = json.dumps(json.loads(file_), indent=4)  # type: ignore

                        else:
                            view_meta["content"] = file_

                view_meta["view_type"] = "code"

            else:
                view_meta["view_type"] = "iframe"

                # get remote path relative to storage root
                file_info["uri"] = storage_client.generate_presigned_url(
                    path=swapped_path.relative_to(storage_root),
                    expiration=PRESIGN_DEFAULT_EXPIRATION,
                )

        return FileViewResponse(file_info=file_info, content=view_meta)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error generating the presigned uri. {error}",
        ) from error


@router.post("/files/readme", name="create_readme")
async def create_readme(
    request: Request,
    payload: ReadMeRequest,
) -> bool:
    """UI route that creates a readme file"""

    try:
        # check name and repo exist before saving
        storage_client: StorageClientBase = request.app.state.storage_client
        registry: CardRegistry = getattr(request.app.state.registries, payload.registry_type)

        cards = registry.list_cards(name=payload.name, repository=payload.repository)

        if not cards:
            logger.warning("No cards found for name {} and repository {}", payload.name, payload.repository)
            return False

        # save payload.content to readme in temp file
        with tempfile.TemporaryDirectory() as tmpdirname:
            lpath = Path(tmpdirname) / "README.md"
            with lpath.open("w") as file_:
                file_.write(payload.content)

            rpath = (
                Path(config.opsml_storage_uri)
                / RegistryTableNames.from_str(payload.registry_type).value
                / payload.repository
                / payload.name
                / lpath.name
            )
            # save to storage
            storage_client.put(lpath, rpath)

        logger.info("Readme file created for {} in {}", payload.name, rpath)

        return True

    except Exception as error:  # pylint: disable=broad-except
        logger.error("Error creating readme file {}", error)
        return False
