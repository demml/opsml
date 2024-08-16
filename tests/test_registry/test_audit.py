from typing import Tuple

import pytest

from opsml.cards import AuditCard, DataCard, ModelCard
from opsml.data import NumpyData
from opsml.model import SklearnModel
from opsml.registry import CardRegistries


def test_audit_card(db_registries: CardRegistries):
    audit_registry = db_registries.audit
    card = AuditCard(name="audit_card", repository="repository", contact="test")

    assert card.business[1].response is None
    card.answer_question(section="business", question_nbr=1, response="response")
    assert card.business[1].response is not None

    # test listing all sections
    card.list_questions()

    # test listing specific section
    card.list_questions(section="business")

    assert card.card_type == "audit"

    audit_registry.register_card(card=card)

    # test loading card
    card = audit_registry.load_card(uid=card.uid)
    assert card.business[1].response == "response"

    # add comment
    card.add_comment(name="test", comment="comment")
    assert len(card.comments) == 1

    for i in ["business", "data_understanding", "data_preparation", "modeling", "evaluation", "deployment", "misc"]:
        assert isinstance(getattr(card, i), dict)


def test_audit_card_failure():
    card = AuditCard(name="audit_card", repository="repository", contact="test")

    with pytest.raises(ValueError):
        card._get_section("not_a_section")

    with pytest.raises(KeyError):
        card.answer_question(section="business", question_nbr=100, response="response")


def test_audit_card_add_uids(db_registries: CardRegistries, linear_regression: Tuple[SklearnModel, NumpyData]):
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
