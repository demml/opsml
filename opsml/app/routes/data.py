from fastapi import APIRouter, Body, HTTPException, Request, status

from opsml.app.core.config import config
from opsml.app.routes.pydantic_models import CardRequest
from opsml.app.routes.utils import replace_proxy_root
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistries, CardRegistry, DataCard
from tempfile import TemporaryDirectory

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()
CHUNK_SIZE = 31457280


@router.post("/data/profile", name="download_data_profile")
def get_data_profile(
    request: Request,
    payload: CardRequest = Body(...),
) -> StreamingResponse:
    """Downloads a datacard profile"""

    registry: CardRegistry = request.app.state.registries.data
    datacard: DataCard = registry.load_card(
        name=payload.name,
        team=payload.team,
        version=payload.version,
        uid=payload.uid,
    )

    if datacard.data_profile is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No data profile available for datacard uid:{payload.uid}",
        )

    else:
        try:
            storage_client = request.app.state.storage_client
            with TemporaryDirectory() as tmp_dir:
                filepath = f"{tmp_dir}/{payload.name}-{payload.version}-profile.html"
                datacard.data_profile.to_file(filepath)
                return StreamingResponse(
                    storage_client.iterfile(
                        file_path=filepath,
                        chunk_size=CHUNK_SIZE,
                    ),
                    media_type="application/octet-stream",
                )

        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"There was an error downloading the file. {error}",
            ) from error
