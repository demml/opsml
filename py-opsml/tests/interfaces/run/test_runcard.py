from opsml.card import RunCard


def test_runcard():
    card = RunCard(repository="test", name="test")


def test_runcard_context():
    with RunCard.start_run(repository="test", name="test") as run:
        print(run)

    a
