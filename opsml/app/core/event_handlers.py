# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable, Union

from fastapi import FastAPI, Response

from opsml.helpers.logging import ArtifactLogger
from opsml.model.registrar import ModelRegistrar
from opsml.registry.registry import CardRegistries
from opsml.settings.config import config
from opsml.storage import client

logger = ArtifactLogger.get_logger()

MiddlewareReturnType = Union[Awaitable[Any], Response]


def _init_rollbar() -> None:
    logger.info("Initializing rollbar")

    rollbar_token = os.getenv("ROLLBAR_TOKEN")

    if rollbar_token is None:
        return None

    import rollbar

    rollbar.init(rollbar_token, config.app_env)
    return None


def _init_registries(app: FastAPI) -> None:
    app.state.registries = CardRegistries()
    app.state.storage_client = client.storage_client
    app.state.model_registrar = ModelRegistrar(client.storage_client)
    app.state.storage_root = config.storage_root


def _shutdown_registries(app: FastAPI) -> None:
    app.state.registries = None
    # app.state.storage_client = None
    # app.state.model_registrar = None


def _log_url_and_storage() -> None:
    logger.info("OpsML tracking url: {}", config.opsml_tracking_uri)
    logger.info("OpsML storage url: {}", config.opsml_storage_uri)
    logger.info("Environment: {}", config.app_env)


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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    start_app_handler(app)()
    yield
    stop_app_handler(app)()
