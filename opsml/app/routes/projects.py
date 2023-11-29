# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os


from typing import Optional, cast

from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from opsml.app.routes.route_helpers import ProjectRouteHelper
from opsml.helpers.logging import ArtifactLogger
from opsml.app.routes.utils import error_to_500

logger = ArtifactLogger.get_logger()

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()
project_route_helper = ProjectRouteHelper()


@router.get("/projects/list/", response_class=HTMLResponse)
@error_to_500
async def project_list_page(request: Request, project: Optional[str] = None, run_uid: Optional[str] = None):
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
    return project_route_helper.get_project_run(request=request, project=project, run_uid=run_uid)
