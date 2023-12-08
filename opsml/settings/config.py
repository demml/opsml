# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional


class OpsmlConfig:
    APP_NAME = "OPSML-API"
    APP_ENV = os.environ.get("APP_ENV", "development")
    STORAGE_URI = os.environ.get("OPSML_STORAGE_URI", f"{os.getcwd()}/mlruns")
    TRACKING_URI = os.environ.get("OPSML_TRACKING_URI", f"sqlite:///{os.getcwd()}/tmp.db")
    PROD_TOKEN = os.environ.get("OPSML_PROD_TOKEN", "staging")

    # API client username / password
    OPSML_USERNAME = os.environ.get("OPSML_USERNAME")
    OPSML_PASSWORD = os.environ.get("OPSML_PASSWORD")

    # The current RUN_ID to load when creating a new project
    OPSML_RUN_ID = os.environ.get("OPSML_RUN_ID")

    def __init__(self) -> None:
        self._proxy_root = os.environ.get("PROXY_ROOT")
        self._is_proxy = True

    @property
    def proxy_root(self) -> Optional[str]:
        return self._proxy_root

    @proxy_root.setter
    def proxy_root(self, root: str) -> None:
        self._proxy_root = root

    @property
    def is_proxy(self) -> bool:
        return self._is_proxy

    @is_proxy.setter
    def is_proxy(self, proxy: bool) -> None:
        self._is_proxy = proxy

    @property
    def is_tracking_local(self) -> bool:
        """Used to determine if an API client will be used.

        If tracking is local, the [server] extra is required.
        """
        return not self.TRACKING_URI.lower().strip().startswith("http")


config = OpsmlConfig()
