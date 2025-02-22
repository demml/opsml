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
            metric1 = Metric(name="test", value=1.0)
            metric2 = Metric(name="test", value=2.0)

            exp.log_metric(name="test", value=1.0)
            exp.log_metrics([metric1, metric2])

            exp.log_parameter(name="test", value=1.0)
            exp.log_parameters([Parameter(name="test", value=1.0)])
