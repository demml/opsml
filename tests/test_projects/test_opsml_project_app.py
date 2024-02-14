import numpy as np
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

        run.log_metric(key="m1", value=1.1)
        run.log_metric(key="m2", value=1.2)

        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6])
        run.log_graph(name="graph2", x=np.ndarray((1, 300)), y=np.ndarray((1, 300)))
        run.log_graph(name="multi1", x=[1, 2, 3], y={"a": [4, 5, 6], "b": [4, 5, 6]})
        run.log_graph(
            name="multi2",
            x=np.ndarray((1, 300)),
            y={"a": np.ndarray((1, 300)), "b": np.ndarray((1, 300))},
        )
        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6], graph_style="scatter")
        nbr_metrics = len(run.metrics)
        info.run_id = run.run_id

    proj = OpsmlProject(info=info)
    runcard = proj.run_card
    # reset metrics to empty dict
    runcard.metrics = {}

    # load metrics
    runcard.load_metrics()
    assert len(runcard.metrics) == nbr_metrics

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
