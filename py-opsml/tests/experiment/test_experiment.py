from opsml.test import OpsmlTestServer
from opsml.experiment import (
    Metric,
    Parameter,
)
from opsml import (  # type: ignore
    start_experiment,
    get_experiment_metrics,
    get_experiment_parameters,
    DataCard,
    ModelCard,
    ModelCardMetadata,
    PandasData,
    SklearnModel,
    Prompt,
    PromptCard,
)
from opsml.card import CardRegistries
import joblib  # type: ignore
from pathlib import Path
import uuid
import shutil
from tests.conftest import WINDOWS_EXCLUDE
import pytest
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


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_experimentcard():
    with OpsmlTestServer():
        cleanup_manually_created_directories()
        with start_experiment(repository="test", log_hardware=True) as exp:
            metric1 = Metric(name="test", value=1.0)
            metric2 = Metric(name="test", value=2.0)

            exp.log_metric(name="test", value=1.0)
            exp.log_metrics([metric1, metric2])

            exp.log_parameter(name="test", value=1.0)
            exp.log_parameters([Parameter(name="test1", value=1.0)])

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

        metrics = get_experiment_metrics(card.uid)

        assert len(metrics) == 3

        # ensure metrics are iterable
        for _ in metrics:
            continue

        # parameters
        parameters = get_experiment_parameters(card.uid)

        assert len(parameters) == 2

        # ensure parameters are iterable
        for _ in parameters:
            continue

    cleanup_manually_created_directories()


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_experimentcard_register(
    pandas_data: PandasData,
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
):
    with OpsmlTestServer(True):
        with start_experiment(repository="test", log_hardware=True) as exp:
            datacard = DataCard(
                interface=pandas_data,
                repository="test",
                name="test",
                tags=["foo:bar", "baz:qux"],
            )
            exp.register_card(datacard)

            assert datacard.experimentcard_uid == exp.card.uid

            modelcard = ModelCard(
                interface=random_forest_classifier,
                repository="test",
                name="test",
                to_onnx=True,
                tags=["foo:bar", "baz:qux"],
                metadata=ModelCardMetadata(
                    datacard_uid=datacard.uid,
                ),
            )
            exp.register_card(modelcard)

            assert modelcard.experimentcard_uid == exp.card.uid

            prompt_card = PromptCard(
                prompt=chat_prompt,
                repository="test",
                name="test",
            )
            exp.register_card(prompt_card)

            assert prompt_card.experimentcard_uid == exp.card.uid

            # test starting a random registry in the experiment context
            # (this is not recommended, but need to test if it causes a tokio::runtime deadlock)
            reg = CardRegistries()

        loaded_card = reg.experiment.load_card(uid=exp.card.uid)

        assert loaded_card.name == exp.card.name
        assert loaded_card.repository == exp.card.repository
        assert loaded_card.tags == exp.card.tags
        assert loaded_card.uid == exp.card.uid
        assert loaded_card.version == exp.card.version

        loaded_card.uids.datacard_uids = [datacard.uid]
        loaded_card.uids.modelcard_uids = [modelcard.uid]
        loaded_card.uids.promptcard_uids = [prompt_card.uid]
