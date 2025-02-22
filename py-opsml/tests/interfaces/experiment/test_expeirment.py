from opsml.card import ExperimentCard
from opsml.test import OpsmlTestServer
from opsml.experiment import start_experiment
import time
# Sets up logging for tests


def _test_experimentcard():
    ExperimentCard(repository="test", name="test")


def test_experimentcard_context():
    with OpsmlTestServer(False):
        with start_experiment(repository="test", log_hardware=True) as exp:
            time.sleep(15)
    a
