# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, List, Optional

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.app.core.config import config
from opsml.app.core.event_handlers import start_app_handler, stop_app_handler
from opsml.app.core.middleware import rollbar_middleware
from opsml.app.routes.router import api_router
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

instrumentator = Instrumentator()


class OpsmlApp:
    def __init__(
        self,
        run_mlflow: bool = True,
        port: int = 8888,
        login: bool = False,
    ):
        self.port = port
        self.run_mlflow = run_mlflow
        self.login = login
        self.app = FastAPI(
            title=config.APP_NAME,
            dependencies=self.get_login(),
        )

        if self.run_mlflow:
            self._initialize_mlflow()

    def get_login(self) -> Optional[List[Any]]:
        """Sets the login dependency for an app if specified"""

        if self.login:
            from opsml.app.core.login import get_current_username

            return [Depends(get_current_username)]
        return None

    def _initialize_mlflow(self):
        from opsml.app.core.initialize_mlflow import initialize_mlflow

        mlflow_config = initialize_mlflow()

        if mlflow_config.MLFLOW_SERVER_SERVE_ARTIFACTS:
            config.is_proxy = True
            config.proxy_root = mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT

    def add_startup(self):
        self.app.add_event_handler("startup", start_app_handler(app=self.app))

    def add_shutdown(self):
        self.app.add_event_handler("shutdown", stop_app_handler(app=self.app))

    def add_instrument(self):
        instrumentator.instrument(self.app).expose(self.app)

    def build_mlflow_app(self):
        from mlflow.server import app as mlflow_flask

        if self.login:
            from wsgi_basic_auth import BasicAuth

            logger.info("Setting login credentials")
            self.app.mount("/", WSGIMiddleware(BasicAuth(mlflow_flask)))

        else:
            self.app.mount("/", WSGIMiddleware(mlflow_flask))

    def add_middleware(self):
        """Add rollbar middleware"""
        self.app.middleware("http")(rollbar_middleware)

    def build_app(self):
        self.app.include_router(api_router)

        if self.run_mlflow:
            self.build_mlflow_app()

        self.add_startup()
        self.add_shutdown()

        self.add_middleware()
        self.add_instrument()

    def run(self):
        """Run FastApi App"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def get_app(self):
        """Returns app for when using directly with gunicorn"""
        self.build_app()

        return self.app


def run_app(run_mlflow: bool = True, login: bool = False):
    return OpsmlApp(run_mlflow=run_mlflow, login=login).get_app()


if __name__ == "__main__":
    run_app()

# TODO (steven) - figure out cli stuff later.
# Gunicorn currently blocks mlflow from running when run as a cli (or maybe its me :) )
# @click.command()
# @click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
# @click.option("--mlflow", default=True, help="Whether to run with mlflow or not")
# @click.option("--login", default=False, is_flag=True, help="Whether to use basic username and password")
# def opsml_uvicorn_server(port: int, mlflow: bool, login: bool) -> None:
#
#    logger.info("Starting ML Server")
#
#    if mlflow:
#        logger.info("Starting mlflow")
#
#        from opsml.app.core.initialize_mlflow import initialize_mlflow
#
#        mlflow_config = initialize_mlflow()
#
#        if mlflow_config.MLFLOW_SERVER_SERVE_ARTIFACTS:
#            config.is_proxy = True
#            config.proxy_root = mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT
#
#    model_api = OpsmlApp(run_mlflow=mlflow, port=port, login=login)
#    model_api.build_app()
#    model_api.run()
#


# @click.command()
# @click.option("--mlflow", default=True, help="Whether to run with mlflow or not")
# @click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
# @click.option("--host", default="0.0.0.0", help="HTTP port. Defaults to 8000")
# @click.option("--workers", default=1, help="Number of workers")
# def opsml_gunicorn_server(mlflow: bool, port: int, workers: int, host: str) -> None:
#
#    from opsml.app.core.initialize_mlflow import initialize_mlflow
#
#    mlflow_config = initialize_mlflow()
#    if mlflow_config.MLFLOW_SERVER_SERVE_ARTIFACTS:
#        config.is_proxy = True
#        config.proxy_root = mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT
#    app = OpsmlApp(run_mlflow=True).get_app()
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
