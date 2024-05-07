# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from pathlib import Path
from typing import Optional, cast

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from opsml import DataInterface
from opsml.app.routes.files import download_artifacts_ui, download_file
from opsml.app.routes.pydantic_models import CardRequest, DataCardMetadata
from opsml.app.routes.route_helpers import DataRouteHelper
from opsml.app.routes.utils import error_to_500
from opsml.cards.data import DataCard
from opsml.registry.registry import CardRegistry
from opsml.types import SaveName
from opsml.types.extra import Suffix

# Constants
TEMPLATE_PATH = Path(__file__).parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATE_PATH)


templates = Jinja2Templates(directory=TEMPLATE_PATH)

data_route_helper = DataRouteHelper()
router = APIRouter()


@router.get("/data/list/", response_class=HTMLResponse)
@error_to_500
async def data_list_homepage(request: Request, repository: Optional[str] = None) -> HTMLResponse:
    """UI home for listing models in model registry

    Args:
        request:
            The incoming HTTP request.
        repository:
            The repository to query
    Returns:
        200 if the request is successful. The body will contain a JSON string
        with the list of models.
    """
    return data_route_helper.get_homepage(request=request, repository=repository)


@router.get("/data/versions/", response_class=HTMLResponse)
@error_to_500
async def data_versions_page(
    request: Request,
    load_profile: bool = False,
    name: Optional[str] = None,
    version: Optional[str] = None,
) -> HTMLResponse:
    if name is None:
        return RedirectResponse(url="/opsml/data/list/")  # type: ignore[return-value]

    return data_route_helper.get_versions_page(
        request=request,
        name=name,
        version=version,
        load_profile=load_profile,
    )


@router.get("/data/versions/uid/")
@error_to_500
async def data_versions_uid_page(request: Request, uid: str) -> HTMLResponse:
    registry: CardRegistry = request.app.state.registries.data
    selected_data = registry.list_cards(uid=uid)[0]

    return await data_versions_page(  # type: ignore
        request=request,
        name=selected_data["name"],
        version=selected_data["version"],
    )


@router.get("/data/download", name="download_data")
def download_data(request: Request, uid: str) -> StreamingResponse:
    """Downloads data associated with a datacard"""

    registry: CardRegistry = request.app.state.registries.data
    datacard = cast(DataCard, registry.load_card(uid=uid))
    load_path = Path(datacard.uri / SaveName.DATA.value).with_suffix(datacard.interface.data_suffix)
    return download_artifacts_ui(request, str(load_path))


@router.get("/data/download/profile", name="download_data_profile")
def download_data_profile(
    request: Request,
    uid: str,
) -> StreamingResponse:
    """Downloads a datacard profile"""

    registry: CardRegistry = request.app.state.registries.data
    datacard = cast(DataCard, registry.load_card(uid=uid))
    load_path = Path(datacard.uri / SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value)
    return download_file(request, str(load_path))


@router.post("/data/card", name="data_card", response_model=DataCardMetadata)
def get_data_card(request: Request, payload: CardRequest) -> DataCardMetadata:
    """Get a data card"""

    registry: CardRegistry = request.app.state.registries.data

    card: DataCard = registry.load_card(
        name=payload.name,
        repository=payload.repository,
        version=payload.version,
        uid=payload.uid,
    )

    data_splits = None
    sql_logic = None
    feature_map = None

    if isinstance(card.interface, DataInterface):
        # if data_splits are not None, convert to json string
        if card.interface.data_splits is not None:
            splits = [data_split.model_dump() for data_split in card.interface.data_splits]
            data_splits = json.dumps(splits, indent=4)

        if card.metadata.feature_map is not None:
            feature_map = {key: val.model_dump() for key, val in card.metadata.feature_map.items()}
            feature_map = json.dumps(feature_map, indent=4)

        sql_logic = card.interface.sql_logic

    return DataCardMetadata(
        name=card.name,
        repository=card.repository,
        contact=card.contact,
        version=card.version,
        uid=card.uid,
        interface_type=card.metadata.interface_type,
        data_splits=data_splits,
        feature_map=feature_map,
        sql_logic=sql_logic,
    )
