from contextlib import asynccontextmanager
from typing import AsyncGenerator

from core.models import OnnxModel
from fastapi import FastAPI

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Running app start handler.")

    # Load onnx model
    model = OnnxModel()
    app.state.model = model

    yield

    logger.info("Running app shutdown handler.")
    app.state.model = None
