from typing import Dict
import pytest
from opsml.registry.sql.registry import CardRegistry
from opsml.registry import DataCard
from opsml.helpers.exceptions import VersionError


def test_version_tags(db_registries: Dict[str, CardRegistry]):
    # create data card
    registry: CardRegistry = db_registries["data"]

    kwargs = {
        "name": "pre_build",
        "team": "mlops",
        "user_email": "opsml.com",
        "sql_logic": {"test": "select * from test_table"},
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

    # this should fail
    kwargs = {
        "name": "pre_build",
        "team": "fail",
        "user_email": "opsml.com",
        "sql_logic": {"test": "select * from test_table"},
    }

    with pytest.raises(ValueError) as ve:
        card = DataCard(**kwargs, version="1.0.0")
        registry.register_card(card=card)
    assert ve.match("Model name already exists for a different team. Try a different name.")
