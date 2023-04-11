# pylint: disable=invalid-envvar-value

from opsml_artifacts.projects.base.types import CardRegistries, ProjectInfo
from opsml_artifacts.registry import CardRegistry
from opsml_artifacts.registry.cards import ProjectCard
from opsml_artifacts.registry.storage.storage_system import StorageClientType


def verify_project_id(project_registry: CardRegistry, info: ProjectInfo):

    projects = project_registry.registry.list_cards(name=info.name, team=info.team)
    if bool(projects):
        return projects[0]["project_id"]

    card = ProjectCard(
        name=info.name,
        team=info.team,
        user_email=info.user_email,
    )
    project_registry.register_card(card=card)

    return card.project_id


def verify_runcard_project_match(
    project_id: str,
    run_id: str,
    runcard_registry: CardRegistry,
):
    run = runcard_registry.registry.list_cards(uid=run_id)[0]

    if run.get("project_id") != project_id:
        raise ValueError(
            f"""
            Run id {run_id} is not associated with project {project_id}.
            Expected project {run.get("project_id")}.
            """
        )


def get_card_registries(storage_client: StorageClientType):

    """Gets CardRegistries to associate with MlFlow experiment"""
    registries = CardRegistries(
        datacard=CardRegistry(registry_name="data"),
        modelcard=CardRegistry(registry_name="model"),
        RunCard=CardRegistry(registry_name="run"),
    )

    # double check
    registries.set_storage_client(storage_client=storage_client)

    return registries
