# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import cast, Optional
import json
import tempfile
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from opsml.app.routes.pydantic_models import CardRequest, CompareCardRequest
from opsml.profile.profile_data import DataProfiler
from opsml.registry import CardRegistry, DataCard
from opsml.app.routes.utils import error_to_500, list_team_name_info

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))


templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()
CHUNK_SIZE = 31457280


@router.get("/data/list/")
@error_to_500
async def data_list_homepage(request: Request, team: Optional[str] = None):
    """UI home for listing models in model registry

    Args:
        request:
            The incoming HTTP request.
        team:
            The team to query
    Returns:
        200 if the request is successful. The body will contain a JSON string
        with the list of models.
    """
    registry: CardRegistry = request.app.state.registries.data

    info = list_team_name_info(registry, team)

    return templates.TemplateResponse(
        "include/data/data.html",
        {
            "request": request,
            "all_teams": info.teams,
            "selected_team": info.selected_team,
            "data": info.names,
        },
    )


@router.get("/data/versions/")
@error_to_500
async def data_versions_page(
    request: Request,
    name: Optional[str] = None,
    version: Optional[str] = None,
    load_profile: Optional[bool] = False,
):
    if name is None:
        return RedirectResponse(url="/opsml/data/list/")

    registry: CardRegistry = request.app.state.registries.data
    versions = registry.list_cards(name=name, as_dataframe=False, limit=50)

    if version is None:
        selected_data = cast(DataCard, registry.load_card(uid=versions[0]["uid"]))
        version = selected_data.version
    else:
        selected_data = cast(DataCard, registry.load_card(name=name, version=version))

    if len(selected_data.data_splits) > 0:
        data_splits = json.dumps(
            [split.model_dump() for split in selected_data.data_splits],
            indent=4,
        )
    else:
        data_splits = None

    data_profile = None
    render_profile = False

    if load_profile:
        if selected_data.metadata.uris.profile_html_uri is not None:
            with tempfile.TemporaryDirectory() as tmp_dir:
                filepath = request.app.state.storage_client.download(
                    selected_data.metadata.uris.profile_html_uri, tmp_dir
                )

                stats = os.stat(filepath)
                if stats.st_size / (1024 * 1024) <= 50:
                    with open(filepath, "r", encoding="utf-8") as html_file:
                        data_profile = html_file.read()
                        render_profile = True

                else:
                    data_profile = "Data profile too large to display. Please download to view."
                    render_profile = False

    return templates.TemplateResponse(
        "include/data/data_version.html",
        {
            "request": request,
            "versions": versions,
            "selected_data": selected_data,
            "selected_version": version,
            "data_splits": data_splits,
            "data_profile": data_profile,
            "render_profile": render_profile,
            "load_profile": load_profile,
        },
    )


@router.get("/data/versions/uid/")
@error_to_500
async def data_versions_uid_page(
    request: Request,
    uid: str,
):
    registry: CardRegistry = request.app.state.registries.data
    selected_data = registry.list_cards(uid=uid)[0]

    return await data_versions_page(
        request=request,
        name=selected_data["name"],
        version=selected_data["version"],
    )


@router.get("/data/profile/view/")
@error_to_500
async def data_versions_profile_page(
    request: Request,
    name: str,
    version: str,
    profile_uri: Optional[str] = None,
):
    if profile_uri is None:
        data_profile = "No profile found"
        render = False
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            filepath = request.app.state.storage_client.download(profile_uri, tmp_dir)

            stats = os.stat(filepath)

            if stats.st_size / (1024 * 1024) <= 50:
                with open(filepath, "r", encoding="utf-8") as html_file:
                    data_profile = html_file.read()
                    render = True

            else:
                data_profile = "Data profile too large to display. Please download to view."
                render = False

    return templates.TemplateResponse(
        "include/data/data_profile.html",
        {
            "request": request,
            "name": name,
            "data_profile": data_profile,
            "version": version,
            "render": render,
        },
    )


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
                file_path=datacard.metadata.uris.profile_html_uri,
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
    os.remove(file_path)


@router.post("/data/compare", name="compare_data_profile")
def compare_data_profile(
    request: Request,
    payload: CompareCardRequest = Body(...),
) -> StreamingResponse:
    """Runs a data comparison for multiple data profiles"""

    registry: CardRegistry = request.app.state.registries.data

    profiles = []

    # make mypy happy
    if payload.uids is not None and bool(payload.uids):
        for uid in payload.uids:
            datacard = cast(DataCard, registry.load_card(uid=uid))

            if datacard.data_profile is not None:
                profiles.append(datacard.data_profile.get_description())
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"No data profile detected for {datacard.uid}",
                )

    elif payload.versions is not None and bool(payload.versions):
        for version in payload.versions:
            datacard = cast(
                DataCard,
                registry.load_card(name=payload.name, version=version),
            )
            if datacard.data_profile is not None:
                profiles.append(datacard.data_profile.get_description())
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"No data profile detected for {datacard.uid}",
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DataCard versions or uids must be lists",
        )

    try:
        comparison = DataProfiler.compare_reports(reports=profiles)
        file_path = f"{datacard.name}-{datacard.team}-comparison.html"
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
