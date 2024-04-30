# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import Any, List, Optional

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.app.core.event_handlers import lifespan
from opsml.app.core.login import get_current_username
from opsml.app.core.middleware import rollbar_middleware
from opsml.app.routes.router import api_router
from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import config
from opsml.types import StorageSystem

logger = ArtifactLogger.get_logger()

instrumentator = Instrumentator()
BUILD_PATH = (Path(__file__).parent / "static" / "site").absolute()


class OpsmlApp:
    def __init__(self, port: int = 8888, login: bool = False):
        self.port = port
        self.login = login
        self.app = FastAPI(title=config.app_name, dependencies=self.get_login(), lifespan=lifespan)

    def get_login(self) -> Optional[List[Any]]:
        """Sets the login dependency for an app if specified"""

        if self.login:
            return [Depends(get_current_username)]
        return None

    def build_app(self) -> None:
        self.app.include_router(api_router)
        self.app.mount("/site", StaticFiles(directory=BUILD_PATH), name="site")
        self.app.mount("/app", StaticFiles(directory=f"{BUILD_PATH}/app"), name="build")

        if config.storage_system == StorageSystem.LOCAL:
            # find path to storage root
            storage_root = Path(config.storage_root)
            storage_root.mkdir(parents=True, exist_ok=True)
            self.app.mount("/artifacts", StaticFiles(directory=config.storage_root), name="artifacts")

        instrumentator.instrument(self.app).expose(self.app)
        self.app.middleware("http")(rollbar_middleware)

    def run(self) -> None:
        """Run FastApi App"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def get_app(self) -> FastAPI:
        """Returns app for when using directly with gunicorn"""
        self.build_app()

        return self.app


def run_app(login: bool = False) -> FastAPI:
    return OpsmlApp(login=login).get_app()


if __name__ == "__main__":
    _ = run_app()
