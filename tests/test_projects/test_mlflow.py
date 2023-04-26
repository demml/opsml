import os
from typing import Any, cast
import pandas as pd
from numpy.typing import NDArray
import pytest
from sklearn import pipeline
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import shutil
from opsml.registry import DataCard, ModelCard
from opsml.registry.cards.types import CardInfo
from opsml.projects.mlflow import MlflowProject, ProjectInfo, MlflowActiveRun
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.helpers.logging import ArtifactLogger
from tests import conftest

logger = ArtifactLogger.get_logger(__name__)


def test_read_only(mlflow_project: MlflowProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")

    with mlflow_project.run() as run:
        # Create metrics / params / cards
        run = cast(MlflowActiveRun, run)
        run.log_metric(key="m1", value=1.1)
        run.log_metric(key="mape", value=2, step=1)
        run.log_metric(key="mape", value=2, step=2)
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

    proj = conftest.mock_mlflow_project(info)
    assert len(proj.metrics) == 2

    assert proj.get_metric("m1").value == 1.1
    assert len(proj.params) == 1
    assert proj.get_param("m1").value == "apple"
    #
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

    opsml_info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com", run_id=info.run_id)
    opsml_project = OpsmlProject(info=opsml_info)

    # Test RunCard
    assert opsml_project.get_metric("m1").value == 1.1
    assert opsml_project.get_param("m1").value == "apple"
    assert opsml_project.datacard_uids[0] == data_card.uid
    assert opsml_project.modelcard_uids[0] == model_card.uid

    with pytest.raises(ValueError):
        # run_id must be associated with correct project
        opsml_info = ProjectInfo(name="test-fail", team="test", user_email="user@test.com", run_id=info.run_id)
        opsml_project = OpsmlProject(info=opsml_info)


def test_metrics(mlflow_project: MlflowProject) -> None:

    info = ProjectInfo(name="test-new", team="test", user_email="user@test.com")
    proj = conftest.mock_mlflow_project(info)
    with proj.run() as run:
        run.log_metric(key="m1", value=1.1)
        info.run_id = run.run_id
    # open the project in read only mode (don't activate w/ context)
    proj = conftest.mock_mlflow_project(info)
    assert len(proj.metrics) == 1
    assert proj.get_metric("m1").value == 1.1


def test_params(mlflow_project: MlflowProject) -> None:

    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with conftest.mock_mlflow_project(info).run() as run:
        run.log_param(key="m1", value="apple")
        info.run_id = run.run_id

    # open the project in read only mode (don't activate w/ context)
    proj = conftest.mock_mlflow_project(info)
    assert len(proj.params) == 1
    assert proj.get_param("m1").value == "apple"


def test_log_artifact(mlflow_project: MlflowProject) -> None:
    filename = "test.png"
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with mlflow_project.run() as run:
        fig, ax = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis
        ax.plot([0, 1, 2], [10, 20, 3])
        array = np.random.random((10, 10))
        fig.savefig("test.png")  # save the figure to file
        plt.close(fig)
        run.log_artifact_from_file(local_path=filename)
        run.log_artifact("test_array", array)
        run.add_tag("test_tag", "1.0.0")
        info.run_id = run.run_id
    # test proxy change

    proj = conftest.mock_mlflow_project(info)
    proj.download_artifacts(artifact_path="misc", local_path="test_path")
    assert os.path.exists("test_path/misc/test_array.joblib")
    assert os.path.exists("test_path/misc/test.png")
    os.remove(filename)
    shutil.rmtree("test_path")  # if assertions pass, this should not fail
    tags = proj.tags
    assert tags["test_tag"] == "1.0.0"


def test_register_load(
    mlflow_project: MlflowProject,
    linear_regression: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with mlflow_project.run() as run:
        model, data = linear_regression
        data_card = DataCard(
            data=data,
            name="linear_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="linear_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
        )
        run.register_card(card=model_card)
        ## Load model card
        loaded_model_card: ModelCard = run.load_card(
            card_type="model",
            info=CardInfo(name="linear_model", team="mlops", user_email="mlops.com"),
        )
        loaded_model_card.load_trained_model()
        assert loaded_model_card.uid is not None
        assert loaded_model_card.trained_model is not None
        # Load data card by uid
        loaded_data_card: DataCard = run.load_card(
            card_type="data", info=CardInfo(name="linear_data", team="mlops", uid=data_card.uid)
        )
        assert loaded_data_card.uid is not None
        assert loaded_data_card.uid == data_card.uid
        info.run_id = run.run_id
        model_uid = loaded_model_card.uid
    proj = conftest.mock_mlflow_project(info)
    loaded_card: ModelCard = proj.load_card(
        card_type="model",
        info=CardInfo(uid=model_uid),
    )
    loaded_card.load_trained_model()


def test_lgb_model(
    mlflow_project: MlflowProject,
    lgb_booster_dataframe: tuple[lgb.Booster, pd.DataFrame],
) -> None:
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with mlflow_project.run() as run:
        model, data = lgb_booster_dataframe
        data_card = DataCard(
            data=data,
            name="lgb_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="lgb_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
        )
        run.register_card(card=model_card)
        info.run_id = run.run_id
    proj = conftest.mock_mlflow_project(info)
    loaded_card: ModelCard = proj.load_card(
        card_type="model",
        info=CardInfo(uid=model_card.uid),
    )
    loaded_card.load_trained_model()


def test_pytorch_model(
    mlflow_project: MlflowProject,
    load_pytorch_resnet: tuple[Any, NDArray],
):
    # another run (pytorch)
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with mlflow_project.run() as run:
        model, data = load_pytorch_resnet
        data_card = DataCard(
            data=data,
            name="resnet_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="resnet_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
        )
        run.register_card(card=model_card)
        info.run_id = run.run_id
    proj = conftest.mock_mlflow_project(info)
    loaded_card: ModelCard = proj.load_card(
        card_type="model",
        info=CardInfo(uid=model_card.uid),
    )
    loaded_card.load_trained_model()


def test_tf_model(
    mlflow_project: MlflowProject,
    load_transformer_example: tuple[Any, NDArray],
):
    # another run (pytorch)
    info = ProjectInfo(name="test-exp", team="test", user_email="user@test.com")
    with mlflow_project.run() as run:
        model, data = load_transformer_example
        data_card = DataCard(
            data=data,
            name="transformer_data",
            team="mlops",
            user_email="mlops.com",
        )
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="transformer_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
        )
        run.register_card(card=model_card)
        info.run_id = run.run_id
    proj = conftest.mock_mlflow_project(info)
    loaded_card: ModelCard = proj.load_card(
        card_type="model",
        info=CardInfo(uid=model_card.uid),
    )
    loaded_card.load_trained_model()
