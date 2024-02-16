# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from fastapi import APIRouter

from opsml.app.routes import (
    audit,
    cards,
    data,
    files,
    healthcheck,
    homepage,
    metrics,
    models,
    projects,
    registry,
)

api_router = APIRouter(responses={404: {"description": "Not found"}})
api_router.include_router(healthcheck.router, tags=["health"], prefix="/opsml")
api_router.include_router(cards.router, tags=["cards"], prefix="/opsml")
api_router.include_router(models.router, tags=["model"], prefix="/opsml")
api_router.include_router(files.router, tags=["file"], prefix="/opsml")
api_router.include_router(data.router, tags=["data"], prefix="/opsml")
api_router.include_router(audit.router, tags=["audit"], prefix="/opsml")
api_router.include_router(homepage.router, tags=["homepage"])
api_router.include_router(registry.router, tags=["registry"], prefix="/opsml")
api_router.include_router(projects.router, tags=["project"], prefix="/opsml")
api_router.include_router(metrics.router, tags=["metrics"], prefix="/opsml")
