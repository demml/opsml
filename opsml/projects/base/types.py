# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from opsml.helpers.types import OpsmlUri
from opsml.registry.utils.settings import settings


class Tags(str, Enum):
    NAME = "name"
    TEAM = "team"
    EMAIL = "user_email"
    VERSION = "version"
    MLFLOW_VERSION = "mlflow.source.git.commit"  # hack for mlflow version


class ProjectInfo(BaseModel):
    """
    A project identifier.

    Projects are identified by a combination of name and team. Each project must
    be unique within a team. The full project identifier is represented as
    "name:team".
    """

    name: str = Field(
        ...,
        description="The project name",
        min_length=1,
    )
    team: str = Field(
        ...,
        description="Team to associate with project",
        min_length=1,
    )
    user_email: Optional[str] = Field(
        None,
        description="Email to associate with project",
        min_length=1,
    )

    run_id: Optional[str] = Field(
        os.environ.get(OpsmlUri.RUN_ID.value),
        description="An existing run_id to use. If None, a new run is created when the project is activated",
    )

    tracking_uri: str = Field(
        settings.opsml_tracking_uri,
        description="Tracking URI. Defaults to OPSML_TRACKING_URI env variable",
    )

    @property
    def project_id(self) -> str:
        """The unique project identifier."""
        return f"{self.team}:{self.name}"

    @property
    def project_name(self) -> str:
        """The project name."""
        return self.name

    @field_validator("name", "team", mode="before")
    def identifier_validator(cls, value: Optional[str]) -> Optional[str]:
        """Lowers and strips an identifier.

        This ensures we don't have any potentially duplicate (by case alone)
        project identifiers."""
        if value is None:
            return None
        return value.strip().lower().replace("_", "-")
