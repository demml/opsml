# pylint: disable=import-outside-toplevel
import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from opsml_artifacts.app.core.config import config
from opsml_artifacts.app.core.event_handlers import start_app_handler, stop_app_handler
from opsml_artifacts.app.core.gunicorn import GunicornApplication
from opsml_artifacts.app.core.middleware import rollbar_middleware
from opsml_artifacts.app.routes.router import api_router
from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

instrumentator = Instrumentator()


class OpsmlApp:
    def __init__(
        self,
        run_mlflow: bool = False,
        port: int = 8080,
    ):
        self.port = port
        self.run_mlflow = run_mlflow
        self.app = FastAPI(title=config.APP_NAME)

    def add_startup(self):
        self.app.add_event_handler("startup", start_app_handler(app=self.app))

    def add_shutdown(self):
        self.app.add_event_handler("shutdown", stop_app_handler(app=self.app))

    def add_instrument(self):
        instrumentator.instrument(self.app).expose(self.app)

    def build_mlflow_app(self):
        from mlflow.server import app as mlflow_flask

        from opsml_artifacts.app.core.initialize_mlflow import initialize_mlflow

        initialize_mlflow()

        if self.login:
            from wsgi_basic_auth import BasicAuth

            self.app.mount("/", WSGIMiddleware(BasicAuth(mlflow_flask)))

        else:
            self.app.mount("/", WSGIMiddleware(mlflow_flask))

    def add_middleware(self):
        """Add rollbar middleware"""
        self.app.middleware("http")(rollbar_middleware)

    def build_app(self):

        self.app.include_router(api_router)
        self.add_startup()
        self.add_shutdown()

        if self.run_mlflow:
            self.build_mlflow_app()

        self.add_instrument()
        self.add_middleware()

    def run(self):
        """Run FastApi App"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def get_app(self):
        """Returns app for when using directly with gunicorn"""
        self.build_app()

        return self.app


@click.command()
@click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
@click.option("--mlflow", default=True, help="Whether to run with mlflow or not")
@click.option("--login", default=False, help="Whether to use basic username and password")
def opsml_uvicorn_server(port: int, mlflow: bool, login: bool) -> None:

    logger.info("Starting ML Server")
    model_api = OpsmlApp(run_mlflow=mlflow, port=port, login=login)
    model_api.build_app()
    model_api.run()


@click.command()
@click.option("--mlflow", default=True, help="Whether to run with mlflow or not")
@click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
@click.option("--host", default="0.0.0.0", help="HTTP port. Defaults to 8000")
@click.option("--workers", default=1, help="Number of workers")
def opsml_gunicorn_server(mlflow: bool, port: int, workers: int, host: str) -> None:

    app = OpsmlApp(run_mlflow=mlflow).get_app()

    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "config": "gunicorn.conf.py",
    }

    logger.info("Starting ML Server")
    GunicornApplication(app, options).run()
