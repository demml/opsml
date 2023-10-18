# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
from pydantic import BaseModel, model_validator, ConfigDict


from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import (
    clean_string,
    validate_name_team_pattern,
)

from opsml.registry.cards.types import (
    CardInfo,
)
from opsml.registry.sql.records import (
    RegistryRecord,
)
from opsml.registry.utils.settings import settings

logger = ArtifactLogger.get_logger()
storage_client = settings.storage_client

SampleModelData = Optional[Union[pd.DataFrame, np.ndarray, Dict[str, np.ndarray], pl.DataFrame]]


class ArtifactCard(BaseModel):
    """Base pydantic class for artifact cards"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
    )

    name: str
    team: str
    user_email: str
    version: Optional[str] = None
    uid: Optional[str] = None
    info: Optional[CardInfo] = None
    tags: Dict[str, str] = {}

    @model_validator(mode="before")
    def validate(cls, env_vars):  # pylint: disable=arguments-renamed
        """Validate base args and Lowercase name and team"""

        card_info = env_vars.get("info")

        for key in ["name", "team", "user_email", "version", "uid"]:
            val = env_vars.get(key)

            if card_info is not None:
                val = val or getattr(card_info, key)

            if key in ["name", "team"]:
                if val is not None:
                    val = clean_string(val)

            env_vars[key] = val

        # validate name and team for pattern
        validate_name_team_pattern(
            name=env_vars["name"],
            team=env_vars["team"],
        )

        return env_vars

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from self attributes"""
        raise NotImplementedError

    def add_tag(self, key: str, value: str):
        self.tags[key] = str(value)

    @property
    def card_type(self) -> str:
        raise NotImplementedError
