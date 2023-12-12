# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class OpsmlConfig(BaseSettings):
    app_name: str = "opsml"
    app_env: str = Field(default="development")

    opsml_storage_uri: str = "./mlruns"
    opsml_tracking_uri: str = "sqlite:///tmp.db"
    opsml_prod_token: str = "staging"

    # API client username / password
    opsml_username: Optional[str] = None
    opsml_password: Optional[str] = None

    # The current RUN_ID to load when creating a new project
    opsml_run_id: Optional[str] = None

    @property
    def is_tracking_local(self) -> bool:
        """Used to determine if an API client will be used.

        If tracking is local, the [server] extra is required.
        """
        return not str(self.opsml_tracking_uri).lower().strip().startswith("http")


config = OpsmlConfig()
