import pandas as pd
import pytest
from sklearn import pipeline

from opsml_artifacts import DataCard, ModelCard
from opsml_artifacts.registry.cards import cards
from opsml_artifacts.projects.mlflow import MlFlowProject, MlFlowProjectInfo
from opsml_artifacts.helpers.logging import ArtifactLogger

from tests import conftest

logger = ArtifactLogger.get_logger(__name__)


def test_read_only(mlflow_project: MlFlowProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]) -> None:
    """Verify that we can read artifacts / metrics / cards without making a run
    active."""

    info = MlFlowProjectInfo(name="test", team="test", user_email="user@test.com")
    with mlflow_project as exp:
        # Create metrics / params / cards
        exp.log_metric(key="m1", value=1.1)
        exp.log_param(key="m1", value="apple")
        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        exp.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid=data_card.uid,
        )
        exp.register_card(card=model_card)
        info.run_id = exp.run_id

    # Retrieve the run and load projects without making the run active (read only mode)
    project = conftest.mock_mlflow_project(info)
    assert len(project.metrics) == 1
    assert project.metrics["m1"] == 1.1
    assert project.params["m1"] == "apple"

    # Load model card
    loaded_card: ModelCard = project.load_card(
        card_type="model",
        info=cards.CardInfo(name="pipeline_model", team="mlops", user_email="mlops.com"),
    )
    loaded_card.load_trained_model()
    assert loaded_card.uid is not None
    assert loaded_card.trained_model is not None

    # Load data card by uid
    loaded_data_card: DataCard = project.load_card(
        card_type="data", info=cards.CardInfo(name="pipeline_data", team="mlops", uid=data_card.uid)
    )
    assert loaded_data_card.uid is not None
    assert loaded_data_card.uid == data_card.uid

    # Attempt to write register cards / log params / log metrics w/o the card being active
    with pytest.raises(ValueError):
        project.register_card(data_card)
    with pytest.raises(ValueError):
        project.log_param(key="param1", value="value1")
    with pytest.raises(ValueError):
        project.log_metric(key="metric1", value=0.0)


def test_metrics(mlflow_project: MlFlowProject) -> None:
    # verify metrics require an ActiveRun

    with pytest.raises(ValueError) as ve:
        mlflow_project.log_metric(key="m1", value=1.0)
    assert ve.match("^ActiveRun")

    info = MlFlowProjectInfo(name="test", team="test", user_email="user@test.com")
    with conftest.mock_mlflow_project(info) as exp:
        exp.log_metric(key="m1", value=1.1)
        info.run_id = exp.run_id

    # open the project in read only mode (don't activate w/ context)
    proj = conftest.mock_mlflow_project(info)
    assert len(proj.metrics) == 1
    assert proj.metrics["m1"] == 1.1


def test_params(mlflow_project: MlFlowProject) -> None:
    # verify params require an ActiveRun
    with pytest.raises(ValueError) as ve:
        mlflow_project.log_metric(key="m1", value=1.1)
    assert ve.match("^ActiveRun")

    info = MlFlowProjectInfo(name="test", team="test", user_email="user@test.com")
    with conftest.mock_mlflow_project(info) as exp:
        exp.log_param(key="m1", value="apple")
        info.run_id = exp.run_id

    # open the project in read only mode (don't activate w/ context)
    proj = conftest.mock_mlflow_project(info)
    assert len(proj.params) == 1
    assert proj.params["m1"] == "apple"


def test_save_load(
    mlflow_project: MlFlowProject,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    with mlflow_project as exp:
        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        exp.register_card(card=data_card)

        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid=data_card.uid,
        )
        exp.register_card(card=model_card)

        # Load model card
        loaded_card: ModelCard = exp.load_card(
            card_type="model",
            info=cards.CardInfo(name="pipeline_model", team="mlops", user_email="mlops.com"),
        )
        loaded_card.load_trained_model()

        assert loaded_card.uid is not None
        assert loaded_card.trained_model is not None

        print(f"uid = {loaded_card.uid}")

        # Load data card by uid
        loaded_data_card: DataCard = exp.load_card(
            card_type="data", info=cards.CardInfo(name="pipeline_data", team="mlops", uid=data_card.uid)
        )
        assert loaded_data_card.uid is not None
        assert loaded_data_card.uid == data_card.uid
