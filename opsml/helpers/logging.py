# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from rusty_logger import Logger, JsonConfig, LogConfig


class ArtifactLogger(Logger):
    @classmethod
    def get_logger(cls) -> Logger:
        return super().get_logger(
            config=LogConfig(
                stdout=True,
                time_format="[year]-[month]-[day]T[hour repr:24]:[minute]:[second]",
                json_config=JsonConfig(),
            ),
        )
