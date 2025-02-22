from opsml.card import ExperimentCard
from opsml.test import OpsmlTestServer
from opsml.experiment import start_experiment, Metric, Parameter
import time
# Sets up logging for tests


def _test_experimentcard():
    ExperimentCard(repository="test", name="test")


def test_experimentcard_context():
    with OpsmlTestServer(False):
        with start_experiment(repository="test", log_hardware=True) as exp:
            with exp.start_experiment(repository="test", log_hardware=True) as _exp2:
                print("hello")
                time.sleep(15)
    a
