from opsml.card import ExperimentCard
from opsml.test import OpsmlTestServer
from opsml.experiment import (
    start_experiment,
    Metric,
    Parameter,
    get_experiment_metrics,
    get_experiment_parameters,
)
import joblib
from pathlib import Path
import uuid
import shutil
# Sets up logging for tests


def cleanup_manually_created_directories():
    shutil.rmtree("artifacts", ignore_errors=True)
    shutil.rmtree("my_path", ignore_errors=True)


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

    for i in range(4):
        fake_data = {"fake": "data"}
        folder = save_path / f"folder_{i}"
        folder.mkdir()

        fake_data_name = save_path / f"folder_{i}" / f"data_{i}.pkl"
        joblib.dump(fake_data, fake_data_name)

    return save_path


def cleanup_fake_directory(save_path: Path):
    shutil.rmtree(save_path)


def _test_experimentcard():
    ExperimentCard(repository="test", name="test")


def test_experimentcard_context():
    with OpsmlTestServer(False):
        cleanup_manually_created_directories()
        with start_experiment(repository="test", log_hardware=True) as exp:
            metric1 = Metric(name="test", value=1.0)
            metric2 = Metric(name="test", value=2.0)

            exp.log_metric(name="test", value=1.0)
            exp.log_metrics([metric1, metric2])

            exp.log_parameter(name="test", value=1.0)
            exp.log_parameters([Parameter(name="test", value=1.0)])

            # create fake items
            file_path = create_fake_file()
            exp.log_artifact(file_path)

            # create fake directory
            dir_path = create_fake_directory()
            exp.log_artifacts(dir_path)

        # cleanup fake items
        cleanup_fake_file(file_path)

        # cleanup fake directory
        cleanup_fake_directory(dir_path)

        card = exp.card

        files = card.list_artifacts()

        assert len(files) == 6

        files = card.list_artifacts("folder_0")

        assert len(files) == 1

        # download all artifacts
        card.download_artifacts()

        # check that "artifacts" directory was created and contains 5 files
        created_path = Path("artifacts")
        assert created_path.exists()

        assert len(list(created_path.iterdir())) == 6

        # attempt to download just one artifact
        card.download_artifacts("folder_0", "my_path")

        # check that "my_path" directory was created and contains 1 file
        created_path = Path("my_path")

        assert created_path.exists()
        assert len(list(created_path.iterdir())) == 1

        # get metrics

        # get parameters

    cleanup_manually_created_directories()

    metrics = get_experiment_metrics(card.uid)

    print(metrics)
    a
