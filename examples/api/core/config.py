import os
from pathlib import Path

from opsml.helpers.logging import ArtifactLogger

logger: ArtifactLogger = ArtifactLogger.get_logger()


class _Config:
    APP_VERSION = "0.0.1"
    APP_NAME = "lightgbm-reg"
    APP_ENV = os.getenv("APP_ENV", "localhost")

    MODEL_NAME = "lightgbm-reg"
    MODEL_PATH = Path("./model")
    MODEL_VERSION = "1.0.0"


Config = _Config()
