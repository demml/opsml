from pathlib import Path
from typing import Tuple

import numpy as np
import pytest
from starlette.testclient import TestClient

from opsml import AuditCard, CardInfo, DataCard, ModelCard, PandasData, SklearnModel
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry.registry import CardRegistries
from opsml.types import Metric

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


def test_opsml_read_only_login(
    api_registries_login: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""

    info = ProjectInfo(name="test-exp", repository="test", contact="user@test.com")
    with OpsmlProject(info=info).run() as run:

        # Create metrics / params / cards
        run.log_metric(key="m1", value=1.1)
        run.log_metric(key="m2", value=1.2)
        run.log_parameter(key="m1", value="apple")
        model, data = sklearn_pipeline
        data_card = DataCard(
            interface=data,
            name="pipeline_data",
            repository="mlops",
            contact="mlops.com",
        )
        nbr_metrics = len(run.metrics)
        run.register_card(card=data_card, version_type="major")

        # test saving run graph
        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6])
        run.log_graph(name="graph2", x=np.ndarray((1, 300)), y=np.ndarray((1, 300)))
        run.log_graph(name="multi1", x=[1, 2, 3], y={"a": [4, 5, 6], "b": [4, 5, 6]})
        run.log_graph(
            name="multi2",
            x=np.ndarray((1, 300_000)),
            y={"a": np.ndarray((1, 300_000)), "b": np.ndarray((1, 300_000))},
        )
        run.log_graph(name="graph", x=[1, 2, 3], y=[4, 5, 6], graph_style="scatter")

        # test invalid graph (> 50 keys for y)
        with pytest.raises(ValueError):
            y = {str(i): [10, 10, 10] for i in range(100)}
            x = [10, 10, 10]
            run.log_graph(name="multi3", x=x, y=y)  # type: ignore

        model_card = ModelCard(
            interface=model,
            name="pipeline_model",
            repository="mlops",
            contact="mlops.com",
            datacard_uid=data_card.uid,
            to_onnx=True,
        )
        run.register_card(card=model_card)

        # save and artifact
        run.log_artifact_from_file(name="cats", local_path="tests/assets/cats.jpg")
        assert run._info.storage_client.exists(Path(run.artifact_uris["cats"].remote_path))
        info.run_id = run.run_id

        assert data_card.metadata.runcard_uid == run.run_id

        auditcard = AuditCard(name="audit_card", repository="repository", contact="test")
        auditcard.add_card(card=data_card)
        auditcard.add_card(card=model_card)
        run.register_card(card=auditcard)

    # Retrieve the run and load artifacts without making the run active (read only mode)
    # NOTE: info contains the run_id created in the above run.
    proj = OpsmlProject(info=info)

    runcard = proj.runcard

    # reset metrics to empty dict
    runcard.metrics = {}

    # load metrics
    runcard.load_metrics()
    assert len(runcard.metrics) == nbr_metrics

    runcard.load_artifacts()

    assert len(proj.metrics) == 2

    metric = proj.get_metric("m1")
    assert isinstance(metric, Metric)

    assert proj.get_metric("m1").value == 1.1  # type: ignore
    assert len(proj.parameters) == 1
    assert proj.get_parameter("m1").value == "apple"  # type: ignore

    # Load model card
    loaded_card: ModelCard = proj.load_card(
        registry_name="model",
        info=CardInfo(name="pipeline_model", contact="mlops.com"),
    )
    loaded_card.load_model()
    assert loaded_card.uid is not None
    assert loaded_card.model is not None

    # Load data card by uid
    loaded_data_card: DataCard = proj.load_card(
        registry_name="data", info=CardInfo(name="pipeline_data", uid=data_card.uid)
    )
    assert loaded_data_card.uid is not None
    assert loaded_data_card.uid == data_card.uid
    assert loaded_data_card.metadata.runcard_uid == proj.run_id

    # load data
    assert loaded_data_card.data is None
    loaded_data_card.load_data()
    assert loaded_data_card.data is not None

    assert run.metrics["m1"][0].value == 1.1
    assert run.parameters["m1"][0].value == "apple"

    # Attempt to write register cards / log params / log metrics w/o the run being active
    with pytest.raises(ValueError):
        run.register_card(data_card)
    with pytest.raises(NotImplementedError):
        run.run_data
    with pytest.raises(ValueError):
        run.log_parameter(key="param1", value="value1")
    with pytest.raises(ValueError):
        run.log_metric(key="metric1", value=0.0)
    with pytest.raises(ValueError):
        proj._run_mgr.verify_active()

    with pytest.raises(ValueError) as ve:
        api_registries_login.project.delete_card(data_card)
    ve.match("ProjectCardRegistry does not support delete_card")

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"])
    assert len(metrics) == 2

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"], names_only=True)
    assert len(metrics) == 2
    for m in metrics:
        assert m in ["m1", "m2"]
