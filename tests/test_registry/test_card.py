from opsml.registry.cards import ArtifactCard
from opsml.registry.cards.types import CardInfo
import os

card_info = CardInfo(name="test", team="opsml", user_email="opsml@email.com")


def test_artifact_card_with_args():

    card = ArtifactCard(
        name=card_info.name,
        team=card_info.team,
        user_email=card_info.user_email,
    )

    assert card.name == card_info.name
    assert card.team == card_info.team
    assert card.user_email == card_info.user_email


def test_artifact_card_without_args():

    card = ArtifactCard(info=card_info)
    assert card.name == card_info.name
    assert card.team == card_info.team
    assert card.user_email == card_info.user_email


def test_artifact_card_with_both():

    card = ArtifactCard(name="override_name", info=card_info)

    assert card.name == "override-name"  # string cleaning
    assert card.team == card_info.team
    assert card.user_email == card_info.user_email
