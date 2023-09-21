# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from rusty_logger import Logger, JsonConfig, LogConfig


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
