import os
from typing import Any, Awaitable, Callable, Union

import rollbar
from fastapi import Response

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

MiddlewareReturnType = Union[Awaitable[Any], Response]


def _init_rollbar():
    logger.info("Initialzing rollbar")
    rollbar.init(
        os.getenv("ROLLBAR_TOKEN"),
        os.getenv("APP_ENV", "development"),
    )


def start_app_handler() -> Callable[[], None]:
    def startup() -> None:
        _init_rollbar()

    return startup


def stop_app_handler() -> Callable[[], None]:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")

    return shutdown
