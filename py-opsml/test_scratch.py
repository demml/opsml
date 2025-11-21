from opsml.card import Card


def test_card_creation():
    card = Card(name="test_card", space="test_space")
    assert card.name == "test_card"
    assert card.space == "test_space"
