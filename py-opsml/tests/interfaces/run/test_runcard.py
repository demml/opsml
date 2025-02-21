from opsml.card import experimentcard
from opsml.test import OpsmlTestServer


def _test_experimentcard():
    card = experimentcard(repository="test", name="test")


def test_experimentcard_context():
    with OpsmlTestServer(False):
        with experimentcard.start_run(repository="test") as run:
            with run.start_run(repository="test") as _run2:
                print("hello")

    a
