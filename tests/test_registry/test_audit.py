from typing import Tuple

import pytest

from opsml.cards import AuditCard, DataCard, ModelCard
from opsml.data import NumpyData
from opsml.model import SklearnModel
from opsml.registry import CardRegistries


def test_audit_card_failure() -> None:
    card = AuditCard(name="audit_card", repository="repository", contact="test")

    with pytest.raises(ValueError):
        card._get_section("not_a_section")

    with pytest.raises(KeyError):
        card.answer_question(section="business", question_nbr=100, response="response")


def test_audit_card_add_uids(db_registries: CardRegistries, linear_regression: Tuple[SklearnModel, NumpyData]) -> None:
    reg, data = linear_regression
    auditcard = AuditCard(name="audit_card", repository="repository", contact="test")

    datacard = DataCard(name="data_card", repository="repository", contact="test", interface=data)
    db_registries.data.register_card(datacard)

    # test 1st path to add uid
    auditcard.add_card(datacard)

    assert auditcard.metadata.datacards[0].name == datacard.name

    # register card
    db_registries.audit.register_card(card=auditcard)

    # create modelcard
    modelcard = ModelCard(
        name="model_card",
        repository="repository",
        contact="test",
        interface=reg,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )
    db_registries.model.register_card(card=modelcard)
