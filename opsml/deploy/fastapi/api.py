from typing import Optional

import click
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.deploy.fastapi.event_handler import start_app_handler, stop_app_handler
from opsml.deploy.fastapi.gunicorn import GunicornApplication
from opsml.deploy.fastapi.middleware import rollbar_middleware
from opsml.deploy.fastapi.routes import RouteCreator
from opsml.deploy.loader import ModelLoader
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

PREDICT_ROUTE = "/predict"

instrumentator = Instrumentator()


class ModelApi:
    def __init__(self, port: int = 8080) -> None:

        self.port = port
        self.app = FastAPI()
        self.predict_route = PREDICT_ROUTE
        self.models = ModelLoader().load_models()
        self.route_creator = self.get_route_creator()
        self.background_tasks: Optional[BackgroundTasks] = None

    def get_route_creator(self):
        return RouteCreator(models=self.models, route=self.predict_route, app=self.app)

    def add_startup(self):
        self.app.add_event_handler("startup", start_app_handler(models=self.models, app=self.app))

    def add_shutdown(self):
        self.app.add_event_handler("shutdown", stop_app_handler(models=self.models, app=self.app))

    def add_middleware(self):
        """Add rollbar middleware"""
        self.app.middleware("http")(rollbar_middleware)

    def add_instrument(self):
        instrumentator.instrument(self.app).expose(self.app)

    def build_api(self):
        self.route_creator.create_model_routes()
        self.add_startup()
        self.add_shutdown()
        self.add_instrument()
        self.add_middleware()

    def run(self):
        """Run FastApi App"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def get_app(self):
        """Returns app for when using directly with gunicorn"""
        self.build_api()

        return self.app


@click.command()
@click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
def deploy_uvicorn(port: int) -> None:

    logger.info("Starting ML Server")
    model_api = ModelApi(port=port)
    model_api.build_api()
    model_api.run()


@click.command()
@click.option("--port", default=8000, help="HTTP port. Defaults to 8000")
@click.option("--host", default="0.0.0.0", help="HTTP port. Defaults to 8000")
@click.option("--workers", default=1, help="Number of workers")
def deploy_gunicorn(port: int, workers: int, host: str) -> None:

    app = ModelApi().get_app()

    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "config": "gunicorn.conf.py",
    }

    logger.info("Starting ML Server")
    GunicornApplication(app, options).run()
