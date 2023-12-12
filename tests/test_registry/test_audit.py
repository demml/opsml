from typing import Dict, Tuple

import pandas as pd
import pytest
from sklearn import linear_model

from opsml.registry import AuditCard, CardRegistry, DataCard, ModelCard, PipelineCard
from opsml.registry.cards import audit_deco


def test_audit_card(
    db_registries: Dict[str, CardRegistry],
):
    audit_registry = db_registries["audit"]
    card = AuditCard(name="audit_card", team="team", user_email="test")

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
    card = AuditCard(name="audit_card", team="team", user_email="test")

    with pytest.raises(ValueError):
        card._get_section("not_a_section")

    with pytest.raises(KeyError):
        card.answer_question(section="business", question_nbr=100, response="response")


def test_audit_card_add_uids(
    db_registries: Dict[str, CardRegistry], linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame]
):
    audit_registry = db_registries["audit"]
    auditcard = AuditCard(name="audit_card", team="team", user_email="test")

    reg, data = linear_regression

    datacard = DataCard(name="data_card", team="team", user_email="test", data=data)
    data_registry = db_registries["data"]
    data_registry.register_card(card=datacard)

    # test 1st path to add uid
    datacard.add_to_auditcard(auditcard=auditcard)

    assert auditcard.metadata.datacards[0].name == datacard.name

    # register card
    audit_registry.register_card(card=auditcard)

    # create modelcard
    modelcard = ModelCard(
        name="model_card",
        team="team",
        user_email="test",
        trained_model=reg,
        sample_input_data=data,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )
    model_registry = db_registries["model"]
    model_registry.register_card(card=modelcard)

    # test 2nd path to add uid
    modelcard.add_to_auditcard(auditcard_uid=auditcard.uid)
    auditcard = audit_registry.load_card(uid=auditcard.uid)
    assert auditcard.metadata.modelcards[0].version == modelcard.version
    assert modelcard.metadata.auditcard_uid == auditcard.uid

    ### These should fail
    with pytest.raises(ValueError):
        modelcard = ModelCard(
            name="model_card",
            team="team",
            user_email="test",
            trained_model=reg,
            sample_input_data=data,
        )
        modelcard.add_to_auditcard(auditcard_uid=auditcard.uid)

    # need to raise other errors
    with pytest.raises(ValueError):
        pipe = PipelineCard(name="pipe", team="team", user_email="test")
        auditcard.add_card(pipe)

    # need fail on unregistered modelcard
    with pytest.raises(ValueError):
        modelcard = ModelCard(
            name="model_card",
            team="team",
            user_email="test",
            trained_model=reg,
            sample_input_data=data,
        )
        auditcard.add_card(modelcard)

    # need fail on unregistered datacard
    with pytest.raises(ValueError):
        datacard = DataCard(name="data_card", team="team", user_email="test", data=data)
        auditcard.add_card(datacard)


def test_audit_deco():
    # calling for coverage
    audit_deco.AuditCard.card_type
    audit_deco.AuditCard.uid

    # test deco
    @audit_deco.auditable
    class Test:
        def __init__(self):
            pass

    assert hasattr(Test, "add_to_auditcard")
