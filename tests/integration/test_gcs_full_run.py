from pathlib import Path
from typing import Tuple

import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.cards import DataCard, ModelCard, RunCard
from opsml.data import PandasData
from opsml.model import ModelInterface
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import CardRegistries, CardRegistry
from opsml.types import RegistryTableNames, SaveName, Suffix


@pytest.mark.parametrize(
    "model_and_data",
    [
        lazy_fixture("sklearn_pipeline"),
    ],
)
def test_gcs_full_run(
    api_registries: CardRegistries,
    model_and_data: Tuple[ModelInterface, PandasData],
):
    """Verifies the full cycle of model and data card persistence.

    Because a profile is saved, data must be PandasData.
    """
    # get data and model
    model, data = model_and_data

    # set registries
    model_registry: CardRegistry = api_registries.model
    data_registry: CardRegistry = api_registries.data
    run_registry: CardRegistry = api_registries.run
    api_storage_client = model_registry._registry.storage_client

    assert model_registry._registry.storage_client is api_storage_client

    # setup project
    try:
        info = ProjectInfo(name="test", repository="test-exp", contact="test")
        project = OpsmlProject(info=info)

        # create run
        with project.run() as run:
            datacard = DataCard(
                interface=data,
                name="test_data",
                repository="mlops",
                contact="mlops.com",
            )
            datacard.create_data_profile()
            run.register_card(card=datacard)
            run.log_metric("test_metric", 10)
            run.log_metrics({"test_metric2": 20})

            modelcard = ModelCard(
                interface=model,
                name="pipeline_model",
                repository="mlops",
                contact="mlops.com",
                tags={"id": "model1"},
                datacard_uid=datacard.uid,
                to_onnx=True,
            )
            run.register_card(modelcard)

        # check run assets
        assert api_storage_client.exists(Path(run.runcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))

        # check data assets
        assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))
        assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
        assert api_storage_client.exists(
            Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value)
        )
        assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value))

        # check model assets
        assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))
        assert api_storage_client.exists(
            Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(model.model_suffix)
        )
        assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))
        assert api_storage_client.exists(
            Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
        )
        assert api_storage_client.exists(
            Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(model.preprocessor_suffix)
        )

        # load cards

        # load datacard
        _datacard: DataCard = data_registry.load_card(uid=datacard.uid)
        _datacard.load_data_profile()
        _datacard.load_data()

        assert _datacard.interface.data is not None
        assert _datacard.interface.data_profile is not None

        # load modelcard
        _modelcard: ModelCard = model_registry.load_card(uid=modelcard.uid)
        _modelcard.load_model()
        _modelcard.load_onnx_model()

        assert _modelcard.interface.model is not None
        assert _modelcard.interface.preprocessor is not None
        assert _modelcard.interface.sample_data is not None
        assert _modelcard.interface.onnx_model is not None

        # load runcard
        _runcard: RunCard = run_registry.load_card(uid=run.runcard.uid)

        assert _runcard.metrics["test_metric"][0].value == 10

        # delete cards

        # delete datacard
        data_registry.delete_card(datacard)

        # delete modelcard
        model_registry.delete_card(modelcard)

        # delete runcard
        run_registry.delete_card(run.runcard)

        # check run assets
        assert len(api_storage_client.find(Path(run.runcard.uri))) == 0

        # check data assets
        assert len(api_storage_client.find(Path(datacard.uri))) == 0

        # check model assets
        assert len(api_storage_client.find(Path(modelcard.uri))) == 0
    finally:
        # need to remove project from gcs
        project_path = Path("opsml-root:/") / RegistryTableNames.PROJECT.value
        api_storage_client.rm(project_path)
