from typing import cast
import pandas as pd

import pytest
from sklearn import pipeline

import matplotlib.pyplot as plt
import numpy as np
from opsml.registry import DataCard, ModelCard
from opsml.registry.cards.types import CardInfo
from opsml.projects.base._active_run import ActiveRun
from opsml.projects import OpsmlProject
from opsml.helpers.logging import ArtifactLogger
from opsml.model.challenger import ModelChallenger, ChallengeInputs


logger = ArtifactLogger.get_logger()

data_info = CardInfo(
    name="pipeline_data",
    team="mlops",
    user_email="mlops.com",
)
model_info = CardInfo(
    name="pipeline_model",
    team="mlops",
    user_email="mlops.com",
)


def test_challenger_no_previous_version(
    opsml_project: OpsmlProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]
) -> None:
    """Test ModelChallenger using one registered model and no champions"""

    with opsml_project.run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        model, data = sklearn_pipeline
        data_card = DataCard(data=data, info=data_info)
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            info=model_info,
            datacard_uid=data_card.uid,
        )
        run.log_metric("mape", 100)
        run.register_card(card=model_card)

    challenger = ModelChallenger(challenger=model_card)
    battle_result = challenger.challenge_champion(metric_name="mape", metric_value=100, lower_is_better=True)

    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_name == "No model"


def test_challenger(opsml_project: OpsmlProject, sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame]) -> None:
    """Test ModelChallenger using challenger and previous champion"""

    with opsml_project.run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        model, data = sklearn_pipeline
        data_card = DataCard(data=data, info=data_info)
        run.register_card(card=data_card)
        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            info=model_info,
            datacard_uid=data_card.uid,
        )

        run.log_metric("mape", 50)
        run.register_card(card=model_card)

    challenger = ModelChallenger(challenger=model_card)

    battle_result = challenger.challenge_champion(
        metric_name="mape",
        metric_value=90,
        lower_is_better=True,
    )
    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_version == "1.0.0"

    # this should load the runcard
    battle_result = challenger.challenge_champion(
        metric_name="mape",
        lower_is_better=True,
    )
    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_version == "1.0.0"


def test_challenger_champion_list(opsml_project: OpsmlProject) -> None:
    """Test ModelChallenger using champion list"""

    modelcard = opsml_project._run_mgr.registries.model.load_card(name="pipeline_model", version="1.1.0")
    runcard = opsml_project._run_mgr.registries.run.load_card(uid=modelcard.metadata.runcard_uid)

    challenger = ModelChallenger(challenger=modelcard)

    model_info.version = "1.0.0"
    champion_info = model_info
    battle_result = challenger.challenge_champion(
        champions=[champion_info],
        metric_name="mape",
        lower_is_better=True,
        metric_value=40,
    )

    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_version == "1.0.0"

    # should fail (model version does not exist)
    with pytest.raises(ValueError):
        model_info.version = "2.0.0"
        champion_info = model_info
        battle_result = challenger.challenge_champion(
            champions=[champion_info],
            metric_name="mape",
            lower_is_better=True,
            metric_value=40,
        )

    with pytest.raises(ValueError):
        challenger = ModelChallenger(challenger=modelcard)
        challenger.challenger_metric

    # should fail. RunCard not registered yet
    with pytest.raises(ValueError):
        model_info.version = "2.0.0"
        champion_info = model_info
        battle_result = challenger.challenge_champion(
            champions=[champion_info],
            metric_name="mape",
            lower_is_better=True,
        )


def test_challenger_fail_no_runcard(
    opsml_project: OpsmlProject,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    """Test ModelChallenger using champion list"""

    model, data = sklearn_pipeline

    datacard = DataCard(data=data, info=data_info)
    opsml_project._run_mgr.registries.data.register_card(card=datacard)

    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=model_info,
        datacard_uid=datacard.uid,
    )
    opsml_project._run_mgr.registries.model.register_card(card=modelcard)

    champion_info = CardInfo(
        name=modelcard.name,
        team=modelcard.team,
        version=modelcard.version,
    )

    # run test
    modelcard = opsml_project._run_mgr.registries.model.load_card(name="pipeline_model", version="1.1.0")
    runcard = opsml_project._run_mgr.registries.run.load_card(uid=modelcard.metadata.runcard_uid)

    challenger = ModelChallenger(challenger=modelcard)

    # should fail (runcard does not exist)
    with pytest.raises(ValueError):
        battle_result = challenger.challenge_champion(
            champions=[champion_info],
            metric_name="mape",
            lower_is_better=True,
            metric_value=100,
        )


def test_challenger_input_validation():
    inputs = ChallengeInputs(
        metric_name=["mae"],
        metric_value=[10],
        lower_is_better=[True],
    )

    with pytest.raises(ValueError):
        ChallengeInputs(
            metric_name=["mae"],
            metric_value=[10],
            lower_is_better=[True, False],
        )
