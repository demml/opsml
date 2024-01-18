import pytest

from opsml.cards import DataCard
from opsml.data import SqlData
from opsml.helpers.exceptions import VersionError
from opsml.registry import CardRegistries
from opsml.registry.registry import CardRegistry


def test_version_tags(sql_data: SqlData, db_registries: CardRegistries):
    registry: CardRegistry = db_registries.data

    kwargs = {
        "name": "pre_build",
        "repository": "mlops",
        "contact": "opsml.com",
        "interface": sql_data,
    }

    # create initial prerelease
    card = DataCard(**kwargs, version="1.0.0")
    registry.register_card(card=card, version_type="pre", pre_tag="prod")
    assert card.version == "1.0.0-prod.1"

    # increment pre-release
    card = DataCard(**kwargs, version="1.0.0")
    registry.register_card(card=card, version_type="pre", pre_tag="prod")
    assert card.version == "1.0.0-prod.2"

    # Switch pre-release to major.minor.patch
    card = DataCard(**kwargs)
    registry.register_card(card=card, version_type="minor")
    assert card.version == "1.0.0"

    card = DataCard(**kwargs, version="1.0.0")
    registry.register_card(card=card, version_type="pre", pre_tag="prod")
    assert card.version == "1.0.0-prod.3"

    # this should fail (version already exists)
    card = DataCard(**kwargs, version="1.0.0")
    with pytest.raises(VersionError) as ve:
        registry.register_card(card=card, version_type="minor")
    assert ve.match("Version combination already exists")

    # add build
    card = DataCard(**kwargs, version="1.0.0")
    registry.register_card(card=card, version_type="pre_build", pre_tag="prod")
    assert card.version == "1.0.0-prod.1+build.1"

    # increment build
    card = DataCard(**kwargs, version="1.0.0")
    registry.register_card(card=card, version_type="build")
    assert card.version == "1.0.0+build.1"

    # increment minor
    card = DataCard(**kwargs)
    registry.register_card(card=card, version_type="patch")
    assert card.version == "1.0.1"

    # this should fail
    with pytest.raises(ValueError) as ve:
        card = DataCard(**kwargs)
        registry.register_card(card=card, version_type="pre")
    assert ve.match("Cannot set pre-release or build tag without a version")

    # set custom vers
    card = DataCard(**kwargs, version="1.0.0+git.1a5d783h3784")
    registry.register_card(card=card, version_type="build")
    assert card.version == "1.0.0+git.1a5d783h3784"


def test_build_tag_official_version(sql_data: SqlData, db_registries: CardRegistries):
    # create data card
    registry: CardRegistry = db_registries.data

    kwargs = {
        "name": "build_tag",
        "repository": "mlops",
        "contact": "opsml.com",
        "interface": sql_data,
    }

    # create card with minor increment with build tag
    card = DataCard(**kwargs)
    registry.register_card(card=card, build_tag="git.1a5d783h3784")
    assert card.version == "1.0.0+git.1a5d783h3784"

    # patch increment
    card = DataCard(**kwargs)
    registry.register_card(card=card, build_tag="git.1a5d783h3784", version_type="patch")
    assert card.version == "1.0.1+git.1a5d783h3784"

    # minor increment
    card = DataCard(**kwargs)
    registry.register_card(card=card, build_tag="git.1a5d783h3784")
    assert card.version == "1.1.0+git.1a5d783h3784"

    # create release candidate for next major
    card = DataCard(**kwargs)
    card.version = "2.0.0"
    registry.register_card(card=card, version_type="pre", pre_tag="rc")
    assert card.version == "2.0.0-rc.1"

    # major increment
    card = DataCard(**kwargs)
    registry.register_card(card=card, build_tag="git.1a5d783h3784", version_type="major")
    assert card.version == "2.0.0+git.1a5d783h3784"

    # major increment
    card = DataCard(**kwargs)
    registry.register_card(card=card, version_type="major")
    assert card.version == "3.0.0"

    # make sure git tags are in list cards
    versions = [card["version"] for card in registry.list_cards(name="build_tag", ignore_release_candidates=True)]
    assert len(versions) == 5  # 6 including one release candidate
