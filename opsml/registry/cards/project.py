# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Optional

from pydantic import field_validator, ValidationInfo


from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import (
    CardType,
)
from opsml.registry.sql.records import (
    ProjectRegistryRecord,
    RegistryRecord,
)
from opsml.registry.utils.settings import settings

logger = ArtifactLogger.get_logger()
storage_client = settings.storage_client


class ProjectCard(ArtifactCard):
    """
    Card containing project information
    """

    project_id: Optional[str] = None

    @field_validator("project_id", mode="before")
    def create_project_id(cls, value, info: ValidationInfo, **kwargs):
        data = info.data  # type: ignore
        return f'{data.get("name")}:{data.get("team")}'

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record for a project"""

        return ProjectRegistryRecord(**self.model_dump())

    @property
    def card_type(self) -> str:
        return CardType.PROJECTCARD.value
