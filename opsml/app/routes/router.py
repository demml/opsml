# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Optional, Sequence

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


def build_router(dependencies: Optional[Sequence[Any]] = None) -> APIRouter:
    api_router = APIRouter(responses={404: {"description": "Not found"}})
    api_router.include_router(healthcheck.router, tags=["health"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(cards.router, tags=["cards"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(models.router, tags=["model"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(files.router, tags=["file"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(data.router, tags=["data"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(audit.router, tags=["audit"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(homepage.router, tags=["homepage"], dependencies=dependencies)
    api_router.include_router(registry.router, tags=["registry"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(projects.router, tags=["project"], prefix="/opsml", dependencies=dependencies)
    api_router.include_router(metrics.router, tags=["metrics"], prefix="/opsml", dependencies=dependencies)

    return api_router
