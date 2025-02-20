from opsml.card import RunCard


def test_runcard():
    card = RunCard(repository="test", name="test")

    print(card.compute_environment)
    a
