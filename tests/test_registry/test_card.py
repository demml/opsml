import pytest

from opsml.helpers.utils import validate_name_team_pattern
from opsml.registry.cards import ArtifactCard
from opsml.registry.cards.types import CardInfo

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


def test_artifact_card_name_team_fail():
    card_info = CardInfo(
        name="i_am_longer_than_53_characters",
        team="team_i_am_longer_than_53_characters",
        user_email="opsml@email.com",
    )

    with pytest.raises(ValueError):
        ArtifactCard(
            name=card_info.name,
            team=card_info.team,
            user_email=card_info.user_email,
        )

    # cards will auto clean name and team, so we need to test the other validation logic with
    # the util func directly
    with pytest.raises(ValueError):
        validate_name_team_pattern(
            name="_invalid_character",
            team="_invalid_character",
        )
