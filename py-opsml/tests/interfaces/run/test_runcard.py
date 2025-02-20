from opsml.card import RunCard
from opsml.test import OpsmlTestServer


def test_runcard():
    card = RunCard(repository="test", name="test")


def test_runcard_context():
    with OpsmlTestServer(True):
        with RunCard.start_run(repository="test") as run:
            # with run.start_run(repository="test") as _run2:
            print("hello")

    a
