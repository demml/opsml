from typing import Tuple

import pytest

from opsml.cards import DataCard, ModelCard
from opsml.data import PandasData
from opsml.helpers.logging import ArtifactLogger
from opsml.model import SklearnModel
from opsml.model.challenger import ChallengeInputs, ModelChallenger
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry.registry import CardRegistries
from opsml.types import CardInfo

logger = ArtifactLogger.get_logger()

data_info = CardInfo(
    name="opsml_data",
    repository="opsml",
    contact="opsml",
)
model_info = CardInfo(
    name="opsml_model",
    repository="opsml",
    contact="opsml",
)


def test_challenger_no_previous_version(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using one registered model and no champions"""
    info = ProjectInfo(name="test", repository="test", contact="test")

    with OpsmlProject(info=info).run() as run:
        # Create metrics / params / cards
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
    battle_result = challenger.challenge_champion(
        metric_name="mape",
        metric_value=100,
        lower_is_better=True,
    )

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


def test_challenge_register_multiple(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using challenger and previous champion"""

    info = ProjectInfo(name="test", repository="test", contact="test")
    for i in range(3):
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

            run.log_metric("mape", i)
            run.register_card(card=model_card)

    challenger = ModelChallenger(challenger=model_card)

    battle_result = challenger.challenge_champion(
        metric_name="mape",
        lower_is_better=False,
    )

    assert battle_result["mape"][0].challenger_win == True
    assert battle_result["mape"][0].champion_version == "1.1.0"

    # register another model without a run
    model_card = ModelCard(
        interface=model,
        info=model_info,
        datacard_uid=data_card.uid,
        to_onnx=True,
    )
    db_registries.model.register_card(model_card)
    assert model_card.version == "1.3.0"

    # run another run
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

        run.log_metric("mape", i)
        run.register_card(card=model_card)

    assert model_card.version == "1.4.0"
    challenger = ModelChallenger(challenger=model_card)

    battle_result = challenger.challenge_champion(
        metric_name="mape",
        lower_is_better=False,
    )

    # should skip over version 1.3.0
    assert battle_result["mape"][0].challenger_win == False
    assert battle_result["mape"][0].champion_version == "1.2.0"


def test_challenge_no_runs(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    """Test ModelChallenger using challenger and previous champion"""

    info = ProjectInfo(name="test", repository="test", contact="test")
    model, data = sklearn_pipeline

    # create models with no runs
    for _ in range(3):
        model_card = ModelCard(
            interface=model,
            info=model_info,
            to_onnx=True,
        )
        db_registries.model.register_card(model_card)

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

        run.log_metric("mape", 10)
        run.register_card(card=model_card)

    challenger = ModelChallenger(challenger=model_card)

    # this should skip over the models with no runs
    battle_result = challenger.challenge_champion(
        metric_name="mape",
        lower_is_better=False,
    )

    assert battle_result["mape"][0].challenger_win == True
    assert battle_result["mape"][0].champion_version == "No version"

    # add champion with different metric
    for i in range(2):
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

            run.log_metric("mae", i)
            run.register_card(card=model_card)

    # challenge champions
    battle_result = challenger.challenge_champion(
        champions=[
            CardInfo(
                name="opsml_model",
                repository="opsml",
                contact="opsml",
                version="1.0.0",
            ),
            CardInfo(
                name="opsml_model",
                repository="opsml",
                contact="opsml",
                version="1.3.0",
            ),
            CardInfo(
                name="opsml_not_exist",
                repository="opsml",
                contact="opsml",
                version="1.3.0",
            ),
            CardInfo(
                name="opsml_model",
                repository="opsml",
                contact="opsml",
                version="1.4.0",
            ),
        ],
        metric_name="mae",
        lower_is_better=True,
        metric_value=40,
    )

    assert battle_result["mae"][0].challenger_win == True
    assert battle_result["mae"][0].champion_version == "no runcard"

    assert battle_result["mae"][1].challenger_win == True
    assert battle_result["mae"][1].champion_version == "metric not found"

    assert battle_result["mae"][2].challenger_win == True
    assert battle_result["mae"][2].champion_version == "model not found"

    assert battle_result["mae"][3].challenger_win == False
    assert battle_result["mae"][3].champion_version == "1.4.0"


def test_challenger_input_validation() -> None:
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
