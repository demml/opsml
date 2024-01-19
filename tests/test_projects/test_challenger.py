from typing import Tuple, cast

import pytest

from opsml.cards import DataCard, ModelCard
from opsml.data import PandasData
from opsml.helpers.logging import ArtifactLogger
from opsml.model import SklearnModel
from opsml.model.challenger import ChallengeInputs, ModelChallenger
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.projects.active_run import ActiveRun
from opsml.registry.registry import CardRegistries
from opsml.types import CardInfo

logger = ArtifactLogger.get_logger()

data_info = CardInfo(
    name="pipeline_data",
    repository="mlops",
    contact="mlops.com",
)
model_info = CardInfo(
    name="pipeline_model",
    repository="mlops",
    contact="mlops.com",
)


def test_challenger_no_previous_version(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using one registered model and no champions"""
    info = ProjectInfo(name="test", repository="test", contact="test")

    with OpsmlProject(info=info).run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        model, data = sklearn_pipeline
        data_card = DataCard(interface=data, info=data_info)
        run.register_card(card=data_card)
        model_card = ModelCard(
            interface=model,
            info=model_info,
            datacard_uid=data_card.uid,
            to_onnx=True,
        )
        run.log_metric("mape", 100)
        run.register_card(card=model_card)

    challenger = ModelChallenger(challenger=model_card)
    battle_result = challenger.challenge_champion(metric_name="mape", metric_value=100, lower_is_better=True)

    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_name == "No model"


def test_challenger(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using challenger and previous champion"""

    info = ProjectInfo(name="test", repository="test", contact="test")
    with OpsmlProject(info=info).run() as run:
        model, data = sklearn_pipeline
        data_card = DataCard(interface=data, info=data_info)
        run.register_card(card=data_card)
        model_card = ModelCard(
            interface=model,
            info=model_info,
            datacard_uid=data_card.uid,
            to_onnx=True,
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
    assert battle_result["mape"][0].champion_version == "No version"

    # this should load the runcard
    battle_result = challenger.challenge_champion(
        metric_name="mape",
        lower_is_better=True,
    )
    assert battle_result["mape"][0].challenger_win
    assert battle_result["mape"][0].champion_version == "No version"


def test_challenger_champion_list(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using champion list"""
    info = ProjectInfo(name="test", repository="test", contact="test")
    with OpsmlProject(info=info).run() as run:
        # Create metrics / params / cards
        run = cast(ActiveRun, run)
        model, data = sklearn_pipeline
        data_card = DataCard(interface=data, info=data_info)
        run.register_card(card=data_card)
        model_card = ModelCard(
            interface=model,
            info=model_info,
            datacard_uid=data_card.uid,
            to_onnx=True,
        )
        run.log_metric("mape", 100)
        run.register_card(card=model_card)

    info = ProjectInfo(name="test", repository="test", contact="test")
    proj = OpsmlProject(info=info)
    modelcard = proj._run_mgr.registries.model.load_card(name="pipeline_model", version="1.0.0")
    proj._run_mgr.registries.run.load_card(uid=modelcard.metadata.runcard_uid)

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


def test_challenger_input_validation():
    ChallengeInputs(
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
