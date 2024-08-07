# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Optional
from opsml.settings.config import config
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


@router.get("/opsml/{path}")
async def opsml_(request: Request, path: str) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            f"site/opsml/{path}.html",
            {"request": request, "path": path},
        )
    except Exception as e:
        logger.error(f"Error rendering UI: {e}")
        raise e


@router.get("/opsml/{path}/card")
async def opsml_card(
    request: Request,
    path: str,
    name: str,
    repository: str,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            f"site/opsml/{path}/card.html",
            {
                "request": request,
                "name": name,
                "repository": repository,
                "version": version,
                "uid": uid,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering UI: {e}")
        raise e


@router.get("/opsml/auth/login")
async def has_auth(request: Request, url: str) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            "site/opsml/auth.html",
            {"request": request, "path": url},
        )
    except Exception as e:
        logger.error(f"Error rendering UI: {e}")
        raise e
