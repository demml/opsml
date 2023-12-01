# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Any, List, Optional

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.app.core.config import config
from opsml.app.core.event_handlers import start_app_handler, stop_app_handler
from opsml.app.core.login import get_current_username
from opsml.app.core.middleware import rollbar_middleware
from opsml.app.routes.router import api_router
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

instrumentator = Instrumentator()
STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))


class OpsmlApp:
    def __init__(
        self,
        port: int = 8888,
        login: bool = False,
    ):
        self.port = port
        self.login = login
        self.app = FastAPI(
            title=config.APP_NAME,
            dependencies=self.get_login(),
        )

    def get_login(self) -> Optional[List[Any]]:
        """Sets the login dependency for an app if specified"""

        if self.login:
            return [Depends(get_current_username)]
        return None

    def build_app(self) -> None:
        self.app.include_router(api_router)
        self.app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

        self.app.add_event_handler("startup", start_app_handler(app=self.app))
        self.app.add_event_handler("shutdown", stop_app_handler(app=self.app))

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

# TODO (steven) - figure out cli stuff later.
# @click.command()
# @click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
# @click.option("--login", default=False, is_flag=True, help="Whether to use basic username and password")
# def opsml_uvicorn_server(port: int, login: bool) -> None:
#
#    logger.info("Starting ML Server")
#
#    model_api = OpsmlApp(port=port, login=login)
#    model_api.build_app()
#    model_api.run()
#


# @click.command()
# @click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
# @click.option("--host", default="0.0.0.0", help="HTTP port. Defaults to 8000")
# @click.option("--workers", default=1, help="Number of workers")
# def opsml_gunicorn_server(port: int, workers: int, host: str) -> None:
#
#
#    app = OpsmlApp().get_app()
#
#    options = {
#        "bind": f"{host}:{port}",
#        "workers": 4,
#        "worker_class": "uvicorn.workers.UvicornWorker",
#        "config": "gunicorn.conf.py",
#        "access-logfile": "-",
#        "error-logfile": "-",
#        "daemon": "true",
#    }
#
#    logger.info("Starting ML Server")
#    GunicornApplication(app, options).run()
