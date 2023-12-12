import os
import sys
from typing import cast

import numpy as np
import pandas as pd
import pytest
from sklearn import pipeline

from opsml.helpers.logging import ArtifactLogger
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.projects._active_run import ActiveRun
from opsml.registry import AuditCard, CardRegistry, DataCard, ModelCard
from opsml.registry.cards.types import CardInfo
from opsml.registry.image import ImageDataset
from tests import conftest

logger = ArtifactLogger.get_logger()


def test_opsml_artifact_storage(opsml_project: OpsmlProject) -> None:
    """Tests logging and retrieving artifacts"""
    with opsml_project.run() as run:
        run.log_artifact("test1", "hello, world")
        run_id = run.run_id

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")

    proj = conftest.mock_opsml_project(info)
    proj.run_id = run_id
    runcard = proj.run_card
    runcard.load_artifacts()

    assert runcard.artifacts.get("test1") is not None
    assert runcard.artifacts.get("test1") == "hello, world"


def test_opsml_read_only(opsml_project: OpsmlProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with opsml_project.run() as run:
        # Create metrics / params / cards
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card, version_type="major")
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
            to_onnx=True,
        )
        run.register_card(card=model_card)

        # save and artifact
        array = np.random.random((10, 10))
        run.log_artifact(name="array", artifact=array)
        info.run_id = run.run_id

        assert data_card.metadata.runcard_uid == run.run_id

        auditcard = AuditCard(name="audit_card", team="team", user_email="test")
        auditcard.add_card(card=data_card)
        auditcard.add_card(card=model_card)
        run.register_card(card=auditcard)

    # Retrieve the run and load artifacts without making the run active (read only mode)
    # NOTE: info contains the run_id created in the above run.
    proj = conftest.mock_opsml_project(info)

    runcard = proj.run_card
    runcard.load_artifacts()
    assert (runcard.artifacts.get("array") == array).all()

    assert len(proj.metrics) == 1
    assert proj.get_metric("m1").value == 1.1
    assert len(proj.parameters) == 1
    assert proj.get_parameter("m1").value == "apple"

    # Load model card
    loaded_card: ModelCard = proj.load_card(
        registry_name="model",
        info=CardInfo(name="pipeline_model", user_email="mlops.com"),
    )
    loaded_card.load_trained_model()
    assert loaded_card.uid is not None
    assert loaded_card.trained_model is not None

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
        proj._run_mgr.active_run
    with pytest.raises(ValueError):
        proj._run_mgr.verify_active()
    with pytest.raises(ValueError):
        info.run_id = "run_id_fail"
        proj = conftest.mock_opsml_project(info)

    proj_reg = CardRegistry("project")

    with pytest.raises(ValueError) as ve:
        proj_reg.delete_card(data_card)
    ve.match("ProjectCardRegistry does not support delete_card")

    with pytest.raises(ValueError) as ve:
        proj_reg.load_card("test-exp")
    ve.match("ProjectCardRegistry does not support load_card")


def test_opsml_continue_run(opsml_project: OpsmlProject) -> None:
    """Verify a run con be continued"""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with opsml_project.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        info.run_id = run.run_id

        assert run.run_name == "test"

    # create new run without re-instantiating opsml project
    with opsml_project.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")
        assert info.run_id != run.run_id

        assert run.run_name == "test"

    new_proj = conftest.mock_opsml_project(info)

    with new_proj.run() as run:
        run = cast(ActiveRun, run)
        run.log_metric(key="m2", value=1.2)
        run.log_parameter(key="m2", value="banana")

    read_project = conftest.mock_opsml_project(info)

    assert len(read_project.metrics) == 2
    assert read_project.get_metric("m1").value == 1.1
    assert read_project.get_metric("m2").value == 1.2
    assert len(read_project.parameters) == 2
    assert read_project.get_parameter("m1").value == "apple"
    assert read_project.get_parameter("m2").value == "banana"


def test_opsml_fail_active_run(opsml_project: OpsmlProject) -> None:
    """Verify starting another run inside another fails"""

    with opsml_project.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)

        with pytest.raises(ValueError):
            with opsml_project.run() as run:
                print("fail")


def test_run_fail(opsml_project: OpsmlProject) -> None:
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")

    with pytest.raises(AttributeError):
        with opsml_project.run(run_name="test") as run:
            run.log_metric(key="m1", value=1.1)
            info.run_id = run.run_id
            opsml_project.fit()  # ATTR doesnt exist

    # open the project in read only mode (don't activate w/ context)
    proj = conftest.mock_opsml_project(info)
    assert len(proj.metrics) == 1
    assert proj.get_metric("m1").value == 1.1

    # Failed run should still exist
    cards = proj._run_mgr.registries.run.list_cards(uid=info.run_id, as_dataframe=False)
    assert len(cards) == 1


def test_opsml_project_list_runs(
    opsml_project_2: OpsmlProject,
) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""

    with opsml_project_2.run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_parameter(key="m1", value="apple")

    assert len(opsml_project_2.list_runs()) == 1


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_opsml_image_dataset(opsml_project: OpsmlProject) -> None:
    """verify we can save image dataset"""

    with opsml_project.run() as run:
        # Create metrics / params / cards
        image_dataset = ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="metadata.jsonl",
        )

        data_card = DataCard(
            data=image_dataset,
            name="image_test",
            team="mlops",
            user_email="mlops.com",
        )

        run.register_card(card=data_card)
        loaded_card = run.load_card(registry_name="data", info=CardInfo(uid=data_card.uid))

        loaded_card.data.image_dir = "test_image_dir"
        loaded_card.load_data()
        assert os.path.isdir(loaded_card.data.image_dir)
        meta_path = os.path.join(loaded_card.data.image_dir, loaded_card.data.metadata)
        assert os.path.exists(meta_path)

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    proj = conftest.mock_opsml_project(info)
    assert len(proj.list_runs()) == 7
