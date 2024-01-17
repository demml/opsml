import pytest

from opsml.cards import ArtifactCard
from opsml.helpers.utils import validate_name_team_pattern
from opsml.types import CardInfo, Comment, RegistryType

card_info = CardInfo(name="test", team="opsml", contact="opsml@email.com")


def test_artifact_card_with_args():
    card = ArtifactCard(
        name=card_info.name,
        team=card_info.team,
        contact=card_info.contact,
    )

    assert card.name == card_info.name
    assert card.team == card_info.team
    assert card.contact == card_info.contact


def test_artifact_card_without_args():
    card = ArtifactCard(info=card_info)
    assert card.name == card_info.name
    assert card.team == card_info.team
    assert card.contact == card_info.contact


def test_artifact_card_with_both():
    card = ArtifactCard(name="override_name", info=card_info)

    assert card.name == "override-name"  # string cleaning
    assert card.team == card_info.team
    assert card.contact == card_info.contact


def test_artifact_card_name_team_fail():
    card_info = CardInfo(
        name="i_am_longer_than_53_characters",
        team="team_i_am_longer_than_53_characters",
        contact="opsml@email.com",
    )

    with pytest.raises(ValueError):
        ArtifactCard(
            name=card_info.name,
            team=card_info.team,
            contact=card_info.contact,
        )

    # cards will auto clean name and team, so we need to test the other validation logic with
    # the util func directly
    with pytest.raises(ValueError):
        validate_name_team_pattern(
            name="_invalid_character",
            team="_invalid_character",
        )


def test_registry_type():
    for i in ["data", "model", "run", "pipeline", "audit", "project"]:
        assert RegistryType.from_str(i) == RegistryType(i)


def test_comment():
    comment1 = Comment(name="foo", comment="bar")
    comment2 = Comment(name="foo", comment="bar")

    assert comment1.__eq__(comment2)
