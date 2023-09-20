# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
import sys
from datetime import datetime
from typing import IO
from typing import Optional
from rusty_logger import Logger, JsonConfig, LogConfig

APP_ENV = os.getenv("APP_ENV", "development")

Logger.get_logger()


class ArtifactLogger(Logger):
    @classmethod
    def get_logger(cls, name: str) -> Logger:
        return super().get_logger(
            name=name,
            config=LogConfig(
                stdout=True,
                json_config=JsonConfig(),
            ),
        )
