import os
from typing import Tuple, cast

import numpy as np
import pytest

from opsml.cards import AuditCard, CardInfo, DataCard, ModelCard
from opsml.data import PandasData
from opsml.model import SklearnModel
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.projects._run_manager import ActiveRunException
from opsml.projects.active_run import ActiveRun
from opsml.registry.registry import CardRegistries


def test_opsml_artifact_storage(db_registries: CardRegistries) -> None:
    """Tests logging and retrieving artifacts"""
    info = ProjectInfo(name="test-exp", repository="test", contact="user@test.com")
    with OpsmlProject(info=info).run() as run:
        run.log_artifact_from_file(name="cats", local_path="tests/assets/cats.jpg")
        run_id = run.run_id
        assert run._info.storage_client.exists(run.artifact_uris["cats"].remote_path)

    proj = OpsmlProject(info=info)
    proj.run_id = run_id
    runcard = proj.runcard
    runcard.load_artifacts()
    assert proj.project_id == 1

    assert run._info.storage_client.exists(runcard.artifact_uris["cats"].local_path)


def test_opsml_read_only(
    db_registries: CardRegistries,
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
            run.log_graph(name="multi3", x=x, y=y)

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
        assert run._info.storage_client.exists(run.artifact_uris["cats"].remote_path)
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
    assert run._info.storage_client.exists(runcard.artifact_uris["cats"].local_path)

    assert len(proj.metrics) == 2
    assert proj.get_metric("m1").value == 1.1
    assert len(proj.parameters) == 1
    assert proj.get_parameter("m1").value == "apple"

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
        db_registries.project.delete_card(data_card)
    ve.match("ProjectCardRegistry does not support delete_card")

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"])
    assert len(metrics) == 2

    metrics = runcard._registry.get_metric(run_uid=info.run_id, name=["m1", "m2"], names_only=True)
    assert len(metrics) == 2
    for m in metrics:
        assert m in ["m1", "m2"]


def test_opsml_continue_run(db_registries: CardRegistries) -> None:
    """Verify a run con be continued"""

    info = ProjectInfo(name="test-exp", repository="test", contact="user@test.com")
    proj = OpsmlProject(info=info)
    with proj.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        run.log_parameters(parameters={"foo": "bar", "bar": "foo"})
        info.run_id = run.run_id
        assert run.run_name == "test"

    # resume write mode
    with proj.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        assert run.run_name == "test"

    new_proj = OpsmlProject(info=info)

    with new_proj.run() as run:
        run = cast(ActiveRun, run)
        run.log_metric(key="m2", value=1.2)
        run.log_parameter(key="m2", value="banana")

    read_project = OpsmlProject(info=info)

    assert len(read_project.metrics) == 2
    assert read_project.get_metric("m1").value == 1.1
    assert read_project.get_metric("m2").value == 1.2
    assert len(read_project.parameters) == 4
    assert read_project.get_parameter("m1").value == "apple"
    assert read_project.get_parameter("m2").value == "banana"
    assert read_project.get_parameter("foo").value == "bar"
    assert read_project.get_parameter("bar").value == "foo"
    runcard = read_project.runcard

    assert runcard.uid == info.run_id
    assert runcard.repository == info.repository
    assert runcard.contact == info.contact


def test_opsml_fail_active_run(db_registries: CardRegistries) -> None:
    """Verify starting another run inside another fails"""

    info = ProjectInfo(name="test-exp", repository="test", contact="user@test.com")
    proj = OpsmlProject(info=info)

    with proj.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)

        with pytest.raises(ActiveRunException):
            with proj.run() as run:
                pass


def test_run_fail(db_registries: CardRegistries) -> None:
    info = ProjectInfo(name="test-exp", repository="test", contact="user@test.com")
    with pytest.raises(AttributeError):
        with OpsmlProject(info).run(run_name="test") as run:
            run.log_metric(key="m1", value=1.1)
            info.run_id = run.run_id
            run.fit()  # ATTR doesnt exist

    # open the project in read only mode (don't activate w/ context)
    proj = OpsmlProject(info=info)
    assert len(proj.metrics) == 1
    assert proj.get_metric("m1").value == 1.1

    # Failed run should still exist
    cards = proj._run_mgr.registries.run.list_cards(
        uid=info.run_id,
    )
    assert len(cards) == 1


def test_opsml_project_list_runs(db_registries: CardRegistries) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""
    info = ProjectInfo(name="list_runs", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)

    with project.run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")

    assert len(OpsmlProject(info=info).list_runs()) > 0


def test_project_card_info_env_var(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Verify that we can set card info via env vars"""

    card_info = CardInfo(name="test-card", repository="opsml", contact="opsml_user").set_env()
    project_info = ProjectInfo(name="test-exp")
    model, data = sklearn_pipeline

    with OpsmlProject(info=project_info).run() as run:
        run = cast(ActiveRun, run)

        # data card should inherit card info from env vars
        datacard = DataCard(interface=data)
        run.register_card(card=datacard)

        # model card should inherit card info from env vars
        modelcard = ModelCard(interface=model, datacard_uid=datacard.uid)
        run.register_card(card=modelcard)

    assert datacard.name == card_info.name
    assert datacard.repository == card_info.repository
    assert datacard.contact == card_info.contact

    assert modelcard.name == card_info.name
    assert modelcard.repository == card_info.repository
    assert modelcard.contact == card_info.contact

    # revert opsml env vars
    for key in ["name", "repository", "contact"]:
        os.environ.pop(f"OPSML_RUNTIME_{key.upper()}", None)


def test_opsml_project_id_creation(db_registries: CardRegistries) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""
    info = ProjectInfo(name="project1", repository="test", contact="user@test.com")
    project = OpsmlProject(info=info)

    with project.run() as run:
        pass

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
