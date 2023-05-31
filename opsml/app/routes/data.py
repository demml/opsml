from typing import cast
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from opsml.app.routes.pydantic_models import CardRequest, CompareCardRequest
from opsml.profile.profile_data import DataProfiler
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistry, DataCard
import tempfile

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


@router.post("/data/profile", name="download_data_profile")
def download_data_profile(
    request: Request,
    payload: CardRequest = Body(...),
) -> StreamingResponse:
    """Downloads a datacard profile"""

    registry: CardRegistry = request.app.state.registries.data
    datacard = cast(
        DataCard,
        registry.load_card(
            name=payload.name,
            team=payload.team,
            version=payload.version,
            uid=payload.uid,
        ),
    )

    if datacard.data_profile is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No data profile available for datacard uid:{payload.uid}",
        )

    try:
        storage_client = request.app.state.storage_client
        return StreamingResponse(
            storage_client.iterfile(
                file_path=datacard.uris.profile_html_uri,
                chunk_size=CHUNK_SIZE,
            ),
            media_type="application/octet-stream",
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error


def iterfile(file_path: str):
    with open(file_path, mode="rb") as file_like:  #
        yield from file_like


@router.post("/data/compare", name="compare_data_profile")
def compare_data_profile(
    request: Request,
    payload: CompareCardRequest = Body(...),
) -> StreamingResponse:
    """Runs a data comparison for multiple data profiles"""

    registry: CardRegistry = request.app.state.registries.data

    profiles = []

    if payload.uids is not None:
        for uid in payload.uids:
            datacard = cast(
                DataCard,
                registry.load_card(
                    uid=uid,
                ),
            )
            profiles.append(datacard.data_profile.get_description())

    elif payload.versions is not None:
        for version in payload.versions:
            datacard = cast(
                DataCard,
                registry.load_card(
                    name=payload.name,
                    team=payload.team,
                    version=version,
                ),
            )
            profiles.append(datacard.data_profile.get_description())

    else:
        raise ValueError("Either a list of uids or versions must be passed")

    try:
        comparison = DataProfiler.compare_reports(reports=profiles)
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = f"{tmpdir}/{datacard.name}-{datacard.team}-comparison.html"
            comparison.to_file(file_path)

        return StreamingResponse(
            iterfile(file_path=file_path),
            media_type="application/octet-stream",
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"There was an error downloading the file. {error}",
        ) from error
