import os
from typing import Any, Awaitable, Callable, Union

import rollbar
from fastapi import FastAPI, Response

from opsml_artifacts.app.core.config import config
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import CardType
from opsml_artifacts.registry.sql.registry import CardRegistry

logger = ArtifactLogger.get_logger(__name__)

MiddlewareReturnType = Union[Awaitable[Any], Response]


class CardRegistries:
    def __init__(self):
        self.data = CardRegistry(registry_name=CardType.DATA.value)
        self.model = CardRegistry(registry_name=CardType.MODEL.value)
        self.experiment = CardRegistry(registry_name=CardType.EXPERIMENT.value)
        self.pipeline = CardRegistry(registry_name=CardType.PIPELINE.value)


def _init_rollbar():
    logger.info("Initialzing rollbar")
    rollbar.init(
        os.getenv("ROLLBAR_TOKEN"),
        os.getenv("APP_ENV", "development"),
    )


def _init_registries(app: FastAPI):
    app.state.registries = CardRegistries()


def _shutdown_registries(app: FastAPI):
    app.state.registries = None


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
