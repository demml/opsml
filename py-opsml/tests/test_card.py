from opsml.card import CardInfo


def test_card_info_initialization():
    card = CardInfo(
        name="Test Card",
        repository="https://github.com/test/repo",
        contact="test@example.com",
        uid="12345",
        version="1.0.0",
        tags={"key1": "value1", "key2": "value2"},
    )
    assert card.name == "Test Card"
    assert card.repository == "https://github.com/test/repo"
    assert card.contact == "test@example.com"
    assert card.uid == "12345"
    assert card.version == "1.0.0"
    assert card.tags == {"key1": "value1", "key2": "value2"}


def test_card_info_default_initialization():
    card = CardInfo()
    assert card.name is None
    assert card.repository is None
    assert card.contact is None
    assert card.uid is None
    assert card.version is None
    assert card.tags is None


def test_card_info_set_env():
    card = CardInfo(
        name="card",
        repository="repo",
        contact="user",
        uid="12345",
        version="1.0.0",
        tags={"key1": "value1", "key2": "value2"},
    )

    card.set_env()

    # this is only used for testing purposes because of the different env contexts between rust and python.
    # It works, but we don't necessarily want to expose this method to the user.
    # So we don't include the method in the .pyi class definition.
    set_vars = card.get_vars()

    assert set_vars["OPSML_RUNTIME_NAME"] == "card"
    assert set_vars["OPSML_RUNTIME_REPOSITORY"] == "repo"
    assert set_vars["OPSML_RUNTIME_CONTACT"] == "user"
