# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Dict
from uuid import UUID

import streaming_form_data
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml.app.core.dependencies import verify_token
from opsml.app.routes.pydantic_models import (
    DeleteFileRequest,
    DeleteFileResponse,
    ListFileRequest,
    ListFileResponse,
)
from opsml.app.routes.utils import (
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.table_names import RegistryTableNames

logger = ArtifactLogger.get_logger()
CHUNK_SIZE = 31457280


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 50  # = 50GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
router = APIRouter()


def verify_path(path: str) -> str:
    """Verifies path only contains registry dir names. This is to prevent arbitrary file
    uploads, downloads, lists and deletes.

    Args:
        path:
            path to file

    Returns:
        path
    """
    # For v1 and v2 all artifacts belong to a registry (exception being mlflow artifacts)
    if any(table_name in path for table_name in [*RegistryTableNames, "model_registry"]):
        return path

    # for v1 mlflow, all artifacts follow a path mlflow:/<run_id>/<artifact_path>/artifacts with artifact_path being a uid
    has_artifacts, has_uuid = False, False
    for split in path.split("/"):
        if split == "artifacts":
            has_artifacts = True
            continue
        try:
            UUID(split, version=4)  # we use uuid4
            has_uuid = True
        except ValueError:
            pass

    if has_uuid and has_artifacts:
        return path

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Path is not a valid registry path",
    )


# upload uses the request object directly which affects OpenAPI docs
@router.post("/upload", name="upload", dependencies=[Depends(verify_token)])
async def upload_file(request: Request) -> Dict[str, str]:  # pragma: no cover
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

    # prevent arbitrary file uploads to random dirs
    # Files can only be uploaded to paths that have a registry dir name
    verify_path(path=write_path)

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


@router.get("/files/download", name="download_file")
def download_file(
    request: Request,
    read_path: str,
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

    # prevent arbitrary file downloads
    # Files can only be downloaded from registry paths
    verify_path(path=read_path)

    try:
        storage_client = request.app.state.storage_client
        return StreamingResponse(
            storage_client.iterfile(
                file_path=read_path,
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
    """Lists files

    Args:
        request:
            request object
        payload:
            `ListFileRequest`

    Returns:
        `ListFileResponse`
    """

    read_path = payload.read_path
    verify_path(path=read_path)

    try:
        storage_client = request.app.state.storage_client
        files = storage_client.list_files(read_path)
        return ListFileResponse(files=files)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error


@router.post("/files/delete", name="delete_files", dependencies=[Depends(verify_token)])
def delete_files(
    request: Request,
    payload: DeleteFileRequest,
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

    # prevent arbitrary lists
    # Files can only be listed from pre-defined registry paths
    read_path = payload.read_path
    verify_path(path=read_path)

    try:
        storage_client = request.app.state.storage_client

        files = list_files(
            request=request,
            payload=ListFileRequest(read_path=payload.read_path),
        )

        # no point of deleting when its empty
        if len(files.files) == 0:
            return DeleteFileResponse(deleted=False)

        storage_client.delete(payload.read_path)
        return DeleteFileResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error deleting files. {error}",
        ) from error
