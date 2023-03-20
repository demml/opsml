import pandas as pd
import pytest
from sklearn import pipeline

from opsml_artifacts import DataCard, ModelCard
from opsml_artifacts.experiments import types
from opsml_artifacts.experiments.mlflow import MlFlowExperiment, MlFlowExperimentInfo
from opsml_artifacts.helpers.logging import ArtifactLogger

from tests import conftest

logger = ArtifactLogger.get_logger(__name__)


def test_metrics(mlflow_experiment: MlFlowExperiment) -> None:
    with pytest.raises(ValueError) as ve:
        mlflow_experiment.log_metric(key="m1", value=1.0)
    assert ve.match("^ActiveRun")

    info = MlFlowExperimentInfo(name="test", team="test", user_email="user@test.com")
    with conftest.mock_mlflow_experiment(info) as exp:
        exp.log_metric(key="m1", value=1.1)
        info.run_id = exp.run_id

    with conftest.mock_mlflow_experiment(info) as exp:
        assert len(exp.metrics) == 1
        assert exp.metrics["m1"] == 1.1


def test_params(mlflow_experiment: MlFlowExperiment) -> None:
    with pytest.raises(ValueError) as ve:
        mlflow_experiment.log_metric(key="m1", value=1.1)
    assert ve.match("^ActiveRun")

    info = MlFlowExperimentInfo(name="test", team="test", user_email="user@test.com")
    with conftest.mock_mlflow_experiment(info) as exp:
        exp.log_param(key="m1", value="apple")
        info.run_id = exp.run_id

    with conftest.mock_mlflow_experiment(info) as exp:
        assert len(exp.params) == 1
        assert exp.params["m1"] == "apple"


def test_save_load(
    mlflow_experiment: MlFlowExperiment,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    with mlflow_experiment as exp:
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

        # Load model card
        exp.register_card(card=model_card)
        loaded_card: ModelCard = exp.load_card(
            card_type="model",
            info=types.CardInfo(name="pipeline_model", team="mlops", user_email="mlops.com"),
        )
        loaded_card.load_trained_model()

        assert loaded_card.uid is not None
        assert loaded_card.trained_model is not None

        print(f"uid = {loaded_card.uid}")

        # Load data card by uid
        loaded_data_card: DataCard = exp.load_card(
            card_type="data", info=types.CardInfo(name="pipeline_data", team="mlops", uid=data_card.uid)
        )
        assert loaded_data_card.uid is not None
        assert loaded_data_card.uid == data_card.uid
