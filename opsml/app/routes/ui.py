# pylint: disable=protected-access

# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# pylint: disable=protected-access

from pathlib import Path
from typing import Optional

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
        return templates.TemplateResponse(name="site/opsml/index.html", request=request)
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error


@router.get("/opsml/{path}")
async def opsml_(request: Request, path: str) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            name=f"site/opsml/{path}.html",
            request=request,
            context={"path": path},
        )
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error


@router.get("/opsml/auth/login")
async def opsml_login(request: Request, url: Optional[str] = None) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            name="site/opsml/auth/login.html",
            request=request,
            context={"path": url},
        )
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error


@router.get("/opsml/{path}/card/{subpath:path}")
async def opsml_card_homepage(
    request: Request,
    path: str,
    subpath: str,
    name: str,
    repository: str,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            name=f"site/opsml/{path}/card/{subpath}.html",
            request=request,
            context={
                "name": name,
                "repository": repository,
                "version": version,
                "uid": uid,
            },
        )
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error


@router.get("/opsml/auth/register")
async def register_page(request: Request, url: Optional[str] = None) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            name="site/opsml/auth/register.html",
            request=request,
            context={"path": url},
        )
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error


@router.get("/opsml/error/page")
async def error_page(request: Request, message: str) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            name="site/opsml/error/page.html",
            request=request,
            context={"message": message},
        )
    except Exception as error:
        logger.error(f"Error rendering UI: {error}")
        raise error
