import pytest

from opsml.cards import ArtifactCard
from opsml.helpers.utils import validate_name_repository_pattern
from opsml.types import CardInfo, Comment, RegistryType

card_info = CardInfo(name="test", repository="opsml", contact="opsml@email.com")


def test_artifact_card_with_args() -> None:
    card = ArtifactCard(
        name=card_info.name,
        repository=card_info.repository,
        contact=card_info.contact,
    )

    assert card.name == card_info.name
    assert card.repository == card_info.repository
    assert card.contact == card_info.contact


def test_artifact_card_without_args() -> None:
    card = ArtifactCard(info=card_info)
    assert card.name == card_info.name
    assert card.repository == card_info.repository
    assert card.contact == card_info.contact


def test_artifact_card_with_both() -> None:
    card = ArtifactCard(name="override_name", info=card_info)

    assert card.name == "override-name"  # string cleaning
    assert card.repository == card_info.repository
    assert card.contact == card_info.contact


def test_artifact_card_name_repository_fail() -> None:
    card_info = CardInfo(
        name="i_am_longer_than_53_characters",
        repository="repository_i_am_longer_than_53_characters",
        contact="opsml@email.com",
    )

    with pytest.raises(ValueError):
        ArtifactCard(
            name=card_info.name,
            repository=card_info.repository,
            contact=card_info.contact,
        )

    # cards will auto clean name and repository, so we need to test the other validation logic with
    # the util func directly
    with pytest.raises(ValueError):
        validate_name_repository_pattern(
            name="_invalid_character",
            repository="_invalid_character",
        )


def test_registry_type() -> None:
    for i in ["data", "model", "run", "pipeline", "audit", "project"]:
        assert RegistryType.from_str(i) == RegistryType(i)


def test_comment() -> None:
    comment1 = Comment(name="foo", comment="bar")
    comment2 = Comment(name="foo", comment="bar")

    assert comment1.__eq__(comment2)


def test_argument_fail() -> None:
    card_info = CardInfo(
        name="name",
        repository="repository",
    )

    with pytest.raises(ValueError):
        ArtifactCard(
            repository=card_info.repository,
            contact=card_info.contact,
        )

    with pytest.raises(ValueError):
        ArtifactCard(
            repository=card_info.repository,
        )

    with pytest.raises(ValueError):
        ArtifactCard(
            info=card_info,
        )
