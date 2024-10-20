# pylint: disable=import-outside-toplevel
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.app.core.event_handlers import lifespan
from opsml.app.core.middleware import rollbar_middleware
from opsml.app.routes import auth
from opsml.app.routes.router import build_router
from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import OpsmlConfig, config
from opsml.types import StorageSystem

logger = ArtifactLogger.get_logger()

instrumentator = Instrumentator()
BUILD_PATH = (Path(__file__).parent / "static" / "site").absolute()


class OpsmlApp:
    def __init__(self, port: int = 8888, app_config: Optional[OpsmlConfig] = None):
        self.port = port
        if app_config is None:
            self.app_config = config
        else:
            self.app_config = app_config

        self.app = FastAPI(title=self.app_config.app_name, lifespan=lifespan)

    def build_app(self) -> None:
        # build routes for the app and include auth deps

        if self.app_config.opsml_auth:
            deps = [Depends(auth.get_current_active_user)]
        else:
            deps = None

        api_router = build_router(dependencies=deps)
        self.app.include_router(api_router)
        self.app.mount("/site", StaticFiles(directory=BUILD_PATH), name="site")
        self.app.mount("/app", StaticFiles(directory=f"{BUILD_PATH}/app"), name="build")

        if self.app_config.storage_system == StorageSystem.LOCAL:
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


def run_app(port: int = 8888, app_config: Optional[OpsmlConfig] = None) -> FastAPI:
    return OpsmlApp(port, app_config).get_app()


if __name__ == "__main__":
    _ = run_app()
