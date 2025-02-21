from opsml.card import ExperimentCard
from opsml.test import OpsmlTestServer
from opsml.experiment import start_experiment


def _test_experimentcard():
    ExperimentCard(repository="test", name="test")


def test_experimentcard_context():
    with OpsmlTestServer(False):
        with start_experiment(repository="test") as exp:
            with exp.start_experiment(repository="test") as _exp2:
                print("hello")

    a
