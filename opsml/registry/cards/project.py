# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#
# IMPORTANT: We need `Dict`, `List`, and `Optional` imported here in order for Pydantic to be able to
# deserialize ProjectCard.
#
from typing import Any, Dict, List, Optional  # noqa # pylint: disable=unused-import

from pydantic import model_validator

from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import CardType
from opsml.registry.sql.records import ProjectRegistryRecord, RegistryRecord


class ProjectCard(ArtifactCard):
    """
    Card containing project information
    """

    project_id: str

    @model_validator(mode="before")
    @classmethod
    def create_project_id(cls, card_args: Dict[str, Any]) -> Dict[str, Any]:
        card_args["project_id"] = f'{card_args["team"]}:{card_args["name"]}'
        return card_args

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record for a project"""

        return ProjectRegistryRecord(**self.model_dump())

    @property
    def card_type(self) -> str:
        return CardType.PROJECTCARD.value
