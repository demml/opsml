# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class OpsmlConfig(BaseSettings):
    APP_NAME: str = "OPSML-API"
    APP_ENV: str = Field(default="development")

    # TODO(@damon): Change these to opsml_
    STORAGE_URI: str = Field(default=f"{os.getcwd()}/mlruns", alias="opsml_storage_uri")
    TRACKING_URI: str = Field(default=f"sqlite:///{os.getcwd()}/tmp.db", alias="opsml_tracking_uri")
    PROD_TOKEN: str = Field(default="staging", alias="opsml_prod_token")

    # API client username / password
    OPSML_USERNAME: Optional[str] = None
    OPSML_PASSWORD: Optional[str] = None

    # The current RUN_ID to load when creating a new project
    OPSML_RUN_ID: Optional[str] = None

    @property
    def is_tracking_local(self) -> bool:
        """Used to determine if an API client will be used.

        If tracking is local, the [server] extra is required.
        """
        return not str(self.TRACKING_URI).lower().strip().startswith("http")


config = OpsmlConfig()
