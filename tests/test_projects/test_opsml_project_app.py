import time

import numpy as np
import pytest
from starlette.testclient import TestClient

from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry.registry import CardRegistries

# test_app already performs a few tests with opsml project in client model
# Adding additional tests here to avoid further cluttering test_app


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
            x=np.ndarray((1, 300_000)),
            y={"a": np.ndarray((1, 300_000)), "b": np.ndarray((1, 300_000))},
        )
        # test invalid graph (> 50 keys for y)
        with pytest.raises(ValueError):
            y = {str(i): [10, 10, 10] for i in range(100)}
            x = [10, 10, 10]
            run.log_graph(name="multi3", x=x, y=y)  # type: ignore

        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6], graph_style="scatter")
        nbr_metrics = len(run.metrics)
        info.run_id = run.run_id

    proj = OpsmlProject(info=info)
    runcard = proj.runcard
    # reset metrics to empty dict
    runcard.metrics = {}

    # load metrics
    runcard.load_metrics()
    assert len(runcard.metrics) == nbr_metrics

    assert project.project_id == 1

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"])
    assert metrics is not None
    assert len(metrics) == 2

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"], names_only=True)
    assert metrics is not None
    assert len(metrics) == 2
    for m in metrics:
        assert m in ["m1", "m2"]  # type: ignore

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


def test_opsml_project_hardware_metric(test_app: TestClient, api_registries: CardRegistries) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""
    info = ProjectInfo(name="project1", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)

    with project.run(log_hardware=True, hardware_interval=10) as run:
        # Create metrics / params / cards
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        time.sleep(15)

    metrics = run.runcard.get_hardware_metrics()
    assert len(metrics) == 1
    assert metrics[0]["run_uid"] == run.run_id
