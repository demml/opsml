# pylint: disable=import-outside-toplevel
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from opsml_artifacts.app.core.config import config
from opsml_artifacts.app.core.event_handlers import start_app_handler, stop_app_handler
from opsml_artifacts.app.routes.router import api_router
from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class OpsmlApp:
    def __init__(self, run_mlflow: bool = False):
        self.run_mlflow = run_mlflow
        self.app = FastAPI(title=config.APP_NAME)

    def build_mlflow_app(self):
        from mlflow.server import app as mlflow_flask

        from opsml_artifacts.app.core.initialize_mlflow import initialize_mlflow

        mlflow_config = initialize_mlflow()
        self.app.mount("/", WSGIMiddleware(mlflow_flask))

        return mlflow_config

    def build_app(self) -> FastAPI:

        self.app.include_router(api_router)
        self.app.add_event_handler("startup", start_app_handler(app=self.app))
        self.app.add_event_handler("shutdown", stop_app_handler(app=self.app))

        if self.run_mlflow:
            mlflow_config = self.build_mlflow_app()
            if mlflow_config.MLFLOW_SERVER_SERVE_ARTIFACTS:
                config.is_proxy = True
                config.proxy_root = mlflow_config.MLFLOW_SERVER_ARTIFACT_ROOT

        return self.app


opsml_app = OpsmlApp(run_mlflow=True).build_app()
