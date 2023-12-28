# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Annotated, Dict, cast

import streaming_form_data
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml.app.core.dependencies import swap_opsml_root, verify_token
from opsml.app.routes.pydantic_models import DeleteFileResponse, ListFileResponse, FileExistsResponse
from opsml.app.routes.utils import (
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.client import StorageClientBase

logger = ArtifactLogger.get_logger()
CHUNK_SIZE = 31457280


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 50  # = 50GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
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

    write_path = Path(swap_opsml_root(write_path))
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)

    if write_path.suffix == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No filename with suffix provided",
        )

    try:
        file_ = ExternalFileTarget(
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
    return {"storage_uri": write_path.as_posix()}


@router.get("/files/download/{read_path}", name="download_file")
def download_file(
    request: Request,
    read_path: Annotated[str, Depends(swap_opsml_root)],
) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        read_path:
            path to file

    Returns:
        Streaming file response
    """
    storage_client: StorageClientBase = cast(StorageClientBase, request.app.state.storage_client)

    try:
        return StreamingResponse(
            storage_client.iterfile(Path(read_path), CHUNK_SIZE),
            media_type="application/octet-stream",
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


@router.get("/files/list/{read_path}", name="list_files")
def list_files(request: Request, read_path: Annotated[str, Depends(swap_opsml_root)]) -> ListFileResponse:
    """Lists files

    Args:
        request:
            request object
        read_path:
            path to read

    Returns:
        `ListFileResponse`
    """
    try:
        storage_client: StorageClientBase = request.app.state.storage_client
        return ListFileResponse(files=storage_client.ls(Path(read_path)))

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error


@router.get("/files/exists/{read_path}", name="download_file")
def file_exists(
    request: Request,
    read_path: Annotated[str, Depends(swap_opsml_root)],
) -> FileExistsResponse:
    """Checks if path exists

    Args:
        request:
            request object
        read_path:
            path to file

    Returns:
        FileExistsResponse
    """
    storage_client: StorageClientBase = cast(StorageClientBase, request.app.state.storage_client)
    return storage_client.exists(Path(read_path))


@router.get("/files/delete/{read_path}", name="delete_files", dependencies=[Depends(verify_token)])
def delete_files(
    request: Request,
    read_path: Annotated[str, Depends(swap_opsml_root)],
) -> DeleteFileResponse:
    """Deletes a file

    Args:
        request:
            request object
        payload:
            `DeleteFileRequest`

    Returns:
        `DeleteFileResponse`
    """

    try:
        storage_client: StorageClientBase = request.app.state.storage_client

        files = list_files(request=request, read_path=read_path)

        # no point of deleting when it's empty
        if len(files.files) == 0:
            return DeleteFileResponse(deleted=False)

        storage_client.rm(Path(read_path))
        return DeleteFileResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error deleting files. {error}",
        ) from error
