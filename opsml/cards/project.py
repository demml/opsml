# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#
# IMPORTANT: We need `Dict`, `List`, and `Optional` imported here in order for Pydantic to be able to
# deserialize ProjectCard.
#
from typing import Any, Dict, List, Optional  # noqa # pylint: disable=unused-import

from opsml.cards.base import ArtifactCard
from opsml.types import CardType


class ProjectCard(ArtifactCard):
    """
    Card containing project information
    """

    project_id: int = 0  # placeholder

    def create_registry_record(self) -> Dict[str, Any]:
        """Creates a registry record for a project"""

        return self.model_dump()

    @property
    def card_type(self) -> str:
        return CardType.PROJECTCARD.value
