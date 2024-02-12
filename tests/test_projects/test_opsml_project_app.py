from starlette.testclient import TestClient

from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry.registry import CardRegistries

# test_app already performs a few tests with opsml project in client model
# Starting to add additional tests here to avoid further cluttering test_app


def test_opsml_project_id_creation(test_app: TestClient, api_registries: CardRegistries) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""
    info = ProjectInfo(name="project1", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)

    with project.run() as run:
         # test saving run graph
        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6])
        run.log_graph(name="graph2", x=np.ndarray((1, 300)), y=np.ndarray((1, 300)))
        run.log_multiline_graph(name="graph1-multi", x=[1, 2, 3], y=[[4, 5, 6], [4, 5, 6]], group_labels=["a", "b"])
        run.log_multiline_graph(
            name="graph1-multi2", x=np.ndarray((1, 300)), y=np.ndarray((2, 300)), group_labels=["a", "b"]
        )

    assert project.project_id == 1

    # create another project
    info = ProjectInfo(name="project2", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)
    with project.run() as run:
        pass

    assert project.project_id == 2

    # resume the first project
    info = ProjectInfo(name="project1", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)

    with project.run() as run:
        pass
    assert project.project_id == 1
