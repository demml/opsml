import os
from typing import Any, Awaitable, Callable, List, Union

import rollbar
from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

from opsml.helpers.logging import ArtifactLogger
from opsml.deploy.loader import Model

logger = ArtifactLogger.get_logger(__name__)

MiddlewareReturnType = Union[Awaitable[Any], Response]


def _init_rollbar():
    logger.info("Initialzing rollbar")
    rollbar.init(
        os.getenv("ROLLBAR_TOKEN"),
        os.getenv("APP_ENV", "development"),
    )


def _add_instrument(app: FastAPI):

    try:
        Instrumentator().instrument(app).expose(app)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.info("Instrument already started. %s", error)


def _start_models(models: List[Model], app: FastAPI) -> None:
    for model in models:
        model_name = f"{model.name}-v{model.version}"
        model.start_onnx_session()
        setattr(app.state, model_name, model)


def _shutdown_models(models: List[Model], app: FastAPI):
    for model in models:
        model_name = f"{model.name}-v{model.version}"
        setattr(app.state, model_name, None)


def start_app_handler(models: List[Model], app: FastAPI) -> Callable[[], None]:
    def startup() -> None:
        _add_instrument(app=app)
        _init_rollbar()
        _start_models(models=models, app=app)

    return startup


def stop_app_handler(models: List[Model], app: FastAPI) -> Callable[[], None]:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_models(models=models, app=app)

    return shutdown
