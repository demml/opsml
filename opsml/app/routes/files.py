# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import io
import tempfile

from pathlib import Path
from typing import Annotated, Dict

import streaming_form_data
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.validators import MaxSizeValidator

from opsml.app.core.dependencies import swap_opsml_root, verify_token
from opsml.app.routes.pydantic_models import (
    DeleteFileResponse,
    FileExistsResponse,
    ListFileResponse,
)
from opsml.app.routes.utils import (
    ExternalFileTarget,
    MaxBodySizeException,
    MaxBodySizeValidator,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.storage import client
import zipfile as zp

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


@router.get("/files/download", name="download_file")
def download_file(path: Annotated[str, Depends(swap_opsml_root)]) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        path:
            path to file

    Returns:
        Streaming file response
    """

    try:
        if Path(path).suffix == "":
            return download_dir(path)

        return StreamingResponse(
            client.storage_client.iterfile(Path(path), CHUNK_SIZE),
            media_type="application/octet-stream",
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


def download_dir(path: Annotated[str, Depends(swap_opsml_root)]) -> StreamingResponse:
    """Downloads a file

    Args:
        request:
            request object
        path:
            path to file

    Returns:
        Streaming file response
    """
    client.storage_client

    try:
        logger.info("Server: Creating zip file for {}", path)
        zip_io = io.BytesIO()

        with tempfile.TemporaryDirectory() as tmpdirname:
            with zp.ZipFile(zip_io, mode="w", compression=zp.ZIP_DEFLATED) as temp_zip:
                lpath = Path(tmpdirname)
                zipfile = lpath / "artifacts"
                rpath = Path(path)
                files = client.storage_client.find(rpath)

                for file_ in files:
                    curr_rpath = Path(file_)
                    curr_lpath = lpath / curr_rpath.relative_to(rpath)
                    logger.info("Server: Downloading {} to {}", curr_rpath, curr_lpath)
                    client.storage_client.get(curr_rpath, curr_lpath)
                    zip_filepath = zipfile / curr_rpath.relative_to(rpath)
                    temp_zip.write(curr_lpath, zip_filepath)

            logger.info("Server: Sending zip file for {}", path)
            return StreamingResponse(
                client.storage_client.iterbuffer(zip_io, CHUNK_SIZE),
                media_type="application/x-zip-compressed",
            )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


@router.get("/files/list", name="list_files")
def list_files(path: Annotated[str, Depends(swap_opsml_root)]) -> ListFileResponse:
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
        return ListFileResponse(files=client.storage_client.find(Path(path)))

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error listing files. {error}",
        ) from error


@router.get("/files/exists", name="file_exists")
def file_exists(path: Annotated[str, Depends(swap_opsml_root)]) -> FileExistsResponse:
    """Checks if path exists

    Args:
        request:
            request object
        read_path:
            path to files

    Returns:
        FileExistsResponse
    """

    return FileExistsResponse(
        exists=client.storage_client.exists(Path(path)),
    )


@router.get("/files/delete", name="delete_files", dependencies=[Depends(verify_token)])
def delete_files(path: Annotated[str, Depends(swap_opsml_root)]) -> DeleteFileResponse:
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
        try:
            client.storage_client.rm(Path(path))
            return DeleteFileResponse(deleted=True)

        except FileNotFoundError:
            logger.warning(f"File {path} not found. It may have already been deleted")
            return DeleteFileResponse(deleted=True)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error deleting files. {error}",
        ) from error
