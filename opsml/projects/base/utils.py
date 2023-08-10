# pylint: disable=invalid-envvar-value
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from opsml.projects.base.types import ProjectInfo
from opsml.registry import CardRegistry
from opsml.registry.cards import ProjectCard


def get_project_id_from_registry(project_registry: CardRegistry, info: ProjectInfo) -> str:
    projects = project_registry.list_cards(
        name=info.name,
        team=info.team,
        as_dataframe=False,
    )
    if bool(projects):
        return projects[0]["project_id"]

    card = ProjectCard(
        name=info.name,
        team=info.team,
        user_email=info.user_email,
    )
    project_registry.register_card(card=card)

    return str(card.project_id)


def verify_runcard_project_match(
    project_id: str,
    run_id: str,
    runcard_registry: CardRegistry,
):
    run = runcard_registry.list_cards(uid=run_id, as_dataframe=False)[0]

    if run.get("project_id") != project_id:
        raise ValueError(
            f"""
            Run id {run_id} is not associated with project {project_id}.
            Expected project {run.get("project_id")}.
            """
        )
