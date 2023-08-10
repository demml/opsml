# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from fastapi import APIRouter

from opsml.app.routes import cards, data, files, healthcheck, models, settings

api_router = APIRouter(responses={404: {"description": "Not found"}})
api_router.include_router(healthcheck.router, tags=["health"], prefix="/opsml")
api_router.include_router(settings.router, tags=["base"], prefix="/opsml")
api_router.include_router(cards.router, tags=["cards"], prefix="/opsml")
api_router.include_router(models.router, tags=["model"], prefix="/opsml")
api_router.include_router(files.router, tags=["file"], prefix="/opsml")
api_router.include_router(data.router, tags=["data"], prefix="/opsml")
