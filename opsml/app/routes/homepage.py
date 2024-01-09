# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Constants
TEMPLATE_PATH = Path(__file__).parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATE_PATH)


templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()


@router.get("/opsml")
async def opsml_homepage(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/opsml/models/list/")


@router.get("/")
async def homepage(request: Request) -> RedirectResponse:
    return RedirectResponse("/opsml")
