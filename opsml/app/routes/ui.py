# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

# Constants
TEMPLATE_PATH = Path(__file__).parents[1] / "static"
templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()


@router.get("/opsml/hello")
async def opsml_homepage(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/opsml/models/list/")


@router.get("/")
async def homepage(request: Request) -> RedirectResponse:
    return RedirectResponse("/opsml")


@router.get("/opsml")
async def opsml_ui(request: Request) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            "site/opsml/index.html",
            {"request": request},
        )
    except Exception as e:
        logger.error(f"Error rendering UI: {e}")
        raise e
