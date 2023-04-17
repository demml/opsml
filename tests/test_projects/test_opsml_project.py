from typing import cast
import pandas as pd

import pytest
from sklearn import pipeline


from opsml.registry import DataCard, ModelCard
from opsml.registry.cards.types import CardInfo
from opsml.projects.base._active_run import ActiveRun
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.helpers.logging import ArtifactLogger
from tests import conftest

logger = ArtifactLogger.get_logger(__name__)


def test_opsml_read_only(opsml_project: OpsmlProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]) -> None:
    """verify that we can read artifacts / metrics / cards without making a run
    active."""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with opsml_project.run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_param(key="m1", value="apple")
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
        )
        run.register_card(card=model_card)
        info.run_id = run.run_id

    # Retrieve the run and load projects without making the run active (read only mode)
    proj = conftest.mock_opsml_project(info)

    assert len(proj.metrics) == 1
    assert proj.metrics["m1"] == 1.1
    assert len(proj.params) == 1
    assert proj.params["m1"] == "apple"

    # Load model card
    loaded_card: ModelCard = proj.load_card(
        card_type="model",
        info=CardInfo(name="pipeline_model", team="mlops", user_email="mlops.com"),
    )
    loaded_card.load_trained_model()
    assert loaded_card.uid is not None
    assert loaded_card.trained_model is not None

    # Load data card by uid
    loaded_data_card: DataCard = proj.load_card(
        card_type="data", info=CardInfo(name="pipeline_data", team="mlops", uid=data_card.uid)
    )
    assert loaded_data_card.uid is not None
    assert loaded_data_card.uid == data_card.uid

    # load data
    assert loaded_data_card.data is None
    loaded_data_card.load_data()
    assert loaded_data_card.data is not None

    # Attempt to write register cards / log params / log metrics w/o the run being active
    with pytest.raises(ValueError):
        run.register_card(data_card)
    with pytest.raises(ValueError):
        run.log_param(key="param1", value="value1")
    with pytest.raises(ValueError):
        run.log_metric(key="metric1", value=0.0)
    with pytest.raises(ValueError):
        proj._run_mgr.active_run
    with pytest.raises(ValueError):
        proj._run_mgr.verify_active()
    with pytest.raises(ValueError):
        info.run_id = "run_id_fail"
        proj = conftest.mock_opsml_project(info)


def test_opsml_continue_run(opsml_project: OpsmlProject) -> None:
    """Verify a run con be continued"""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with opsml_project.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_param(key="m1", value="apple")
        info.run_id = run.run_id

    new_proj = conftest.mock_opsml_project(info)

    with new_proj.run() as run:
        run = cast(ActiveRun, run)
        run.log_metric(key="m2", value=1.2)
        run.log_param(key="m2", value="banana")

    read_project = conftest.mock_opsml_project(info)

    assert len(read_project.metrics) == 2
    assert read_project.metrics["m1"] == 1.1
    assert read_project.metrics["m2"] == 1.2
    assert len(read_project.params) == 2
    assert read_project.params["m1"] == "apple"
    assert read_project.params["m2"] == "banana"


def test_opsml_fail_active_run(opsml_project: OpsmlProject) -> None:
    """Verify starting another run inside another fails"""

    with opsml_project.run(run_name="test") as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)

        with pytest.raises(ValueError):
            with opsml_project.run() as run:
                print("fail")
