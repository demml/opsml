import os
from typing import Any, Awaitable, Callable, Union

import rollbar
from fastapi import FastAPI, Response

from opsml.app.core.config import config
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.model.registrar import ModelRegistrar
from opsml.registry.sql.registry import CardRegistries
from opsml.registry.sql.registry_base import (
    settings,  # importing settings from already initialized registry base
)
from opsml.registry.sql.registry_base import initializer

logger = ArtifactLogger.get_logger(__name__)

MiddlewareReturnType = Union[Awaitable[Any], Response]


def _init_rollbar():
    logger.info("Initializing rollbar")
    rollbar.init(
        os.getenv("ROLLBAR_TOKEN"),
        os.getenv("APP_ENV", "development"),
    )


def _init_registries(app: FastAPI):
    app.state.registries = CardRegistries()
    app.state.storage_client = settings.storage_client
    app.state.model_registrar = ModelRegistrar(settings.storage_client)

    initializer.initialize()


def _shutdown_registries(app: FastAPI):
    app.state.registries = None
    app.state.storage_client = None
    app.state.model_registrar = None


def _log_url_and_storage():
    logger.info("OpsML tracking url: %s", config.TRACKING_URI)
    logger.info("OpsML storage url: %s", config.STORAGE_URI)
    logger.info("Environment: %s", config.APP_ENV)


def start_app_handler(app: FastAPI) -> Callable[[], None]:
    def startup() -> None:
        _log_url_and_storage()
        _init_rollbar()
        _init_registries(app=app)

    return startup


def stop_app_handler(app: FastAPI) -> Callable[[], None]:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_registries(app=app)

    return shutdown
