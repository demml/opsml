# pylint: disable=W0223

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict, Union

from fastapi import FastAPI
from gunicorn.app.base import BaseApplication


class GunicornApplication(BaseApplication):  # type: ignore
    def __init__(  # type: ignore
        self,
        app: FastAPI,
        options=Dict[str, Union[str, int]],
    ) -> None:
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> FastAPI:
        return self.application
