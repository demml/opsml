# pylint: disable=protected-access

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))


templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()


@router.get("/opsml")
async def opsml_homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@router.get("/")
async def homepage(request: Request, mlflow: bool = False):
    if not mlflow:
        return RedirectResponse("/opsml")
    return RedirectResponse("/mlflow/")
