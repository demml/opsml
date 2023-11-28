# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from opsml.app.routes.route_helpers import ModelRouteHelper
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()
model_route_helper = ModelRouteHelper()
