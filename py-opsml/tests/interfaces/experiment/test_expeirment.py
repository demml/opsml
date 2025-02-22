from opsml.card import ExperimentCard
from opsml.test import OpsmlTestServer
from opsml.experiment import start_experiment, Metric, Parameter
import joblib
from pathlib import Path
import uuid
import shutil
# Sets up logging for tests


def create_fake_file() -> Path:
    random_name = uuid.uuid4().hex
    # create fake items
    fake_data = {"fake": "data"}
    save_path = Path(f"{random_name}.pkl")
    joblib.dump(fake_data, save_path)

    return save_path


def cleanup_fake_file(save_path: Path):
    save_path.unlink()


def create_fake_directory() -> Path:
    random_name = uuid.uuid4().hex
    save_path = Path(f"{random_name}")
    save_path.mkdir()

    for i in range(5):
        fake_data = {"fake": "data"}
        fake_data_name = save_path / f"data_{i}.pkl"
        joblib.dump(fake_data, fake_data_name)

    return save_path


def cleanup_fake_directory(save_path: Path):
    shutil.rmtree(save_path)


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

            # create fake items
            save_path = create_fake_file()
            exp.log_artifact(save_path)

            # create fake directory
            save_path = create_fake_directory()
            exp.log_artifacts(save_path)

        # cleanup fake items
        cleanup_fake_file(save_path)

        # cleanup fake directory
        cleanup_fake_directory(save_path)
