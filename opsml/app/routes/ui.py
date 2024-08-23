# pylint: disable=protected-access

# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
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


@router.get("/")
async def homepage(request: Request) -> RedirectResponse:
    return RedirectResponse("/opsml")


@router.get("/opsml/index")
async def index(request: Request) -> RedirectResponse:
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


@router.get("/opsml/error")
async def opsml_error_page(request: Request, error: str) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            "site/opsml/error.html",
            {"request": request, "error": error},
        )
    except Exception as e:
        logger.error(f"Error rendering UI: {e}")
        raise e
