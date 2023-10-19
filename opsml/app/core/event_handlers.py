# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Any, Awaitable, Callable, Union

import rollbar
from fastapi import FastAPI, Response

from opsml.app.core.config import config
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.model.registrar import ModelRegistrar
from opsml.registry.sql.registry import CardRegistries
from opsml.registry.sql.sql_schema import RegistryTableNames
from opsml.registry.utils.settings import settings
from opsml.registry.sql.db_initializer import DBInitializer

logger = ArtifactLogger.get_logger()

MiddlewareReturnType = Union[Awaitable[Any], Response]

# set up db initializer
initializer = DBInitializer(
    engine=settings.sql_engine,
    registry_tables=list(RegistryTableNames),
)


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
    # app.state.storage_client = None
    # app.state.model_registrar = None


def _log_url_and_storage():
    logger.info("OpsML tracking url: {}", config.TRACKING_URI)
    logger.info("OpsML storage url: {}", config.STORAGE_URI)
    logger.info("Environment: {}", config.APP_ENV)


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
