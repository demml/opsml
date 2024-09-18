import uuid
from pathlib import Path
from typing import Any, Dict, Tuple, cast
from unittest import mock

import pytest
from scouter import DriftConfig
from sklearn.preprocessing import LabelEncoder
from starlette.testclient import TestClient

from opsml.app.routes.utils import error_to_500, list_repository_name_info
from opsml.cards import (
    AuditCard,
    DataCard,
    DataCardMetadata,
    ModelCard,
    PipelineCard,
    RunCard,
)
from opsml.data import NumpyData, PandasData, TorchData
from opsml.model import HuggingFaceModel, SklearnModel
from opsml.registry import CardRegistries, CardRegistry
from opsml.settings.config import config
from opsml.storage import client
from opsml.storage.api import ApiRoutes
from opsml.types import Metric, Param, SaveName
from opsml.types.extra import Suffix
from tests.conftest import EXCLUDE, TODAY_YMD


def test_debug(test_app: TestClient) -> None:
    """Test debug path"""

    response = test_app.get("/opsml/debug")

    assert "test.db" in response.json()["url"]
    assert "opsml_registries" in response.json()["storage"]
    assert response.status_code == 200


def test_register_data(
    test_app: TestClient,
    api_registries: CardRegistries,
    api_storage_client: client.StorageClient,
    pandas_data: PandasData,
) -> None:
    assert pandas_data.data is not None

    # encode data
    encoder = LabelEncoder()
    pandas_data.data["animals"] = encoder.fit_transform(pandas_data.data["animals"])

    # create data card
    registry = api_registries.data
    datacard = DataCard(
        interface=pandas_data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    datacard.create_data_profile()
    registry.register_card(card=datacard)

    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    _ = registry.list_cards(name=datacard.name, repository=datacard.repository, max_date=TODAY_YMD)

    _ = registry.list_cards(name=datacard.name)

    _ = registry.list_cards()

    _ = registry.list_cards(sort_by_timestamp=True)

    # Verify repositories / names
    repositories = registry._registry.unique_repositories
    assert "mlops" in repositories

    names = registry._registry.get_unique_card_names(repository="mlops")
    assert "test-df" in names

    info = list_repository_name_info(registry=registry, repository="mlops")
    assert info.repositories is not None
    assert "mlops" in info.repositories

    assert info.names is not None
    assert "test-df" in info.names

    info = list_repository_name_info(registry=registry)
    assert info.repositories is not None
    assert "mlops" in info.repositories
    assert info.names is not None
    assert "test-df" in info.names

    # test ui routes for cards
    response = test_app.get("/opsml/data")
    assert response.status_code == 200

    # test ui routes for cards
    response = test_app.get(
        f"/opsml/data/card/home?name={datacard.name}&repository={datacard.repository}&version={datacard.version}&uid={datacard.uid}"
    )
    assert response.status_code == 200


def test_register_major_minor(api_registries: CardRegistries, numpy_data: NumpyData) -> None:
    # create data card
    registry = api_registries.data

    data_card = DataCard(
        interface=numpy_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.1.1",
    )

    registry.register_card(card=data_card)

    data_card = DataCard(
        interface=numpy_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.1",
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.1.2"

    data_card = DataCard(
        interface=numpy_data,
        name="major_minor",
        repository="mlops",
        contact="mlops.com",
        version="3.1",
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.2.0"


def test_semver_registry_list(
    api_registries: CardRegistries,
    numpy_data: NumpyData,
    test_app: TestClient,
) -> None:
    # create data card
    registry = api_registries.data

    data_card = DataCard(
        interface=numpy_data,
        name="test_array",
        repository="mlops",
        contact="mlops.com",
    )

    registry.register_card(card=data_card)

    # version 2
    data_card = DataCard(
        interface=numpy_data,
        name="test_array",
        repository="mlops",
        contact="mlops.com",
    )
    registry.register_card(card=data_card, version_type="major")

    for i in range(0, 12):
        data_card = DataCard(
            interface=numpy_data,
            name="test_array",
            repository="mlops",
            contact="mlops.com",
        )
        registry.register_card(card=data_card)

    # should return 13 versions
    cards = registry.list_cards(
        name=data_card.name,
        repository=data_card.repository,
        version="2.*.*",
    )
    assert len(cards) == 13

    cards = registry.list_cards(
        name=data_card.name,
        repository=data_card.repository,
        version="^2.3.0",
    )
    assert len(cards) == 1

    cards = registry.list_cards(
        name=data_card.name,
        repository=data_card.repository,
        version="~2.3.0",
    )
    assert len(cards) == 1

    response = test_app.get(
        url="opsml/cards/registry/stats",
        params={"registry_type": registry.registry_type.value},
    )
    assert response.status_code == 200

    response = test_app.get(
        url="opsml/cards/registry/stats",
        params={
            "registry_type": registry.registry_type.value,
            "search_term": "test_array",
        },
    )
    assert response.status_code == 200

    response = test_app.get(
        url="opsml/cards/registry/query/page",
        params={"registry_type": registry.registry_type.value},
    )
    assert response.status_code == 200

    response = test_app.get(
        url="opsml/cards/registry/query/page",
        params={
            "registry_type": registry.registry_type.value,
            "repository:": "mlops",
            "search_term": "test_array",
        },
    )
    assert response.status_code == 200


def test_runcard(
    linear_regression: Tuple[SklearnModel, NumpyData],
    api_registries: CardRegistries,
    api_storage_client: client.StorageClient,
) -> None:
    registry = api_registries.run
    model, data = linear_regression

    run = RunCard(name="run", contact="mlops.com", datacard_uids=["test_uid"], uid=uuid.uuid4().hex)
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    metric1 = run.get_metric("test_metric")
    assert isinstance(metric1[0], Metric)

    metric2 = run.get_metric("test_metric2")
    assert isinstance(metric2[0], Metric)

    assert metric1[0].value == 10
    assert metric2[0].value == 20

    # parameters
    run.log_parameter("test_param", 10)
    run.log_parameters({"test_param2": 20})

    param1 = run.get_parameter("test_param")
    param2 = run.get_parameter("test_param2")
    assert isinstance(param1[0], Param)
    assert isinstance(param2[0], Param)

    # save artifacts
    run.log_artifact_from_file(name="cats", local_path="tests/assets/cats.jpg")
    assert api_storage_client.exists(Path(run.artifact_uris["cats"].remote_path))
    registry.register_card(card=run)

    # Load the card and verify artifacts / metrics
    loaded_card: RunCard = registry.load_card(uid=run.uid)
    assert loaded_card.uid == run.uid
    assert loaded_card.get_metric("test_metric")[0].value == 10
    assert loaded_card.get_metric("test_metric2")[0].value == 20
    loaded_card.load_artifacts()


def test_register_model_data(
    api_registries: CardRegistries,
    populate_model_data_for_api: Tuple[ModelCard, DataCard],
    api_storage_client: client.StorageClient,
) -> None:
    model_registry = api_registries.model
    data_registry = api_registries.data
    modelcard, datacard = populate_model_data_for_api

    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(datacard.interface.data_suffix))

    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))

    loaded_card: ModelCard = model_registry.load_card(uid=modelcard.uid)
    loaded_card.load_model()
    assert loaded_card.model is not None
    assert loaded_card.sample_data is not None

    modelcard_fail = ModelCard(
        interface=modelcard.interface,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=None,
        to_onnx=True,
    )
    model_registry.register_card(card=modelcard_fail)

    # test card tags
    cards = model_registry.list_cards(name=modelcard.name, repository=modelcard.repository, tags=modelcard.tags)

    assert cards[0]["tags"] == {"id": "model1"}

    # load data
    loaded_data: DataCard = data_registry.load_card(name=datacard.name, version=datacard.version)
    loaded_data.load_data()

    assert loaded_data.data is not None

    # update
    loaded_data.version = "1.2.0"
    data_registry.update_card(card=loaded_data)

    record = data_registry.query_value_from_card(uid=str(loaded_data.uid), columns=["version", "timestamp"])
    assert record["version"] == "1.2.0"

    # test assertion error
    with pytest.raises(ValueError):
        DataCard(  # type: ignore
            name=datacard.name,
            repository=datacard.repository,
            contact=datacard.contact,
            metadata=DataCardMetadata(additional_info={"input_metadata": 20}),
        )


def test_pipeline_registry(api_registries: CardRegistry) -> None:
    pipeline_card = PipelineCard(
        name="test_df",
        repository="mlops",
        contact="mlops.com",
        pipeline_code_uri="test_pipe_uri",
    )
    for card_type in ["data", "run", "model"]:
        pipeline_card.add_card_uid(uid=uuid.uuid4().hex, card_type=card_type)

    # register
    registry = api_registries.pipeline
    registry.register_card(card=pipeline_card)
    loaded_card: PipelineCard = registry.load_card(uid=pipeline_card.uid)
    loaded_card.add_card_uid(uid="updated_uid", card_type="data")
    registry.update_card(card=loaded_card)
    registry.list_cards(uid=loaded_card.uid)
    values = registry.query_value_from_card(
        uid=loaded_card.uid,
        columns=["datacard_uids"],
    )
    assert bool(values["datacard_uids"])


def test_download_model_metadata_failure(test_app: TestClient) -> None:
    response = test_app.post(url=f"opsml/{ApiRoutes.MODEL_METADATA}", json={"name": "pip"})

    # should fail
    assert response.status_code == 500
    assert response.json()["detail"] == "Model not found"


def test_model_metrics(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    modelcard, _, _ = populate_model_data_for_route
    response = test_app.post(url=f"/opsml/{ApiRoutes.METRICS}", json={"run_uid": modelcard.metadata.runcard_uid})

    metrics = response.json()["metric"]

    assert metrics[0]["name"] == "m1"
    assert metrics[0]["value"] == 1.1


@pytest.mark.skipif(EXCLUDE, reason="Skipping")
def test_token_fail(
    monkeypatch: pytest.MonkeyPatch,
    api_registries: CardRegistries,
) -> None:
    monkeypatch.setattr(config, "app_env", "production")
    monkeypatch.setattr(config, "opsml_prod_token", "fail")
    run = RunCard(
        name="test_df",
        repository="mlops",
        contact="mlops.com",
        datacard_uids=["test_uid"],
    )

    with pytest.raises(
        ValueError,
        match="Cannot perform write operation on prod resource without token",
    ):
        api_registries.run.register_card(card=run)


def test_delete_fail(test_app: TestClient) -> None:
    response = test_app.get("/opsml/files/delete", params={"path": "opsml-root:/OPSML_DATA_REGISTRY/notthere"})

    assert response.status_code == 200
    cast(Dict[str, Any], response.json())

    # Invaild path: does not include a registry table
    response = test_app.get("/opsml/files/delete", params={"path": "notthere"})
    assert response.status_code == 500


def test_card_create_fail(test_app: TestClient) -> None:
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/create",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_update_fail(test_app: TestClient) -> None:
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/update",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_list_fail(test_app: TestClient) -> None:
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/list",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


##### Test ui routes
def test_ui(test_app: TestClient) -> None:
    """Test settings"""

    response = test_app.get("/opsml")
    assert response.status_code == 200

    response = test_app.get("/opsml")
    assert response.status_code == 200

    response = test_app.get("/opsml/error/page?message=blah")
    assert response.status_code == 200

    response = test_app.get("/opsml/auth/login")
    assert response.status_code == 200

    response = test_app.get("/opsml/auth/register")
    assert response.status_code == 200


def test_error_wrapper() -> None:
    @error_to_500
    async def fail(request):  # type: ignore
        raise ValueError("Fail")

    fail("fail")


def test_registry_name_fail(test_app: TestClient) -> None:
    response = test_app.get(
        "/opsml/registry/table",
        params={"registry_type": "blah"},
    )

    assert response.status_code == 500


def test_upload_fail(test_app: TestClient) -> None:
    headers = {
        "Filename": "blah:",
        "WritePath": "fake",
        "X-Prod-Token": "test-token",
    }
    files = {"file": open("tests/assets/cats.jpg", "rb")}

    response = test_app.post(
        url=f"opsml/{ApiRoutes.UPLOAD_FILE}",
        files=files,
        headers=headers,
    )

    assert response.status_code == 422


def test_download_fail(test_app: TestClient) -> None:
    # test register model (onnx)
    response = test_app.get(url=f"opsml/{ApiRoutes.DOWNLOAD_FILE}?read_path=fake")
    assert response.status_code == 422


@pytest.mark.skipif(EXCLUDE, reason="Skipping")
def test_register_vit(
    test_app: TestClient,
    api_registries: CardRegistries,
    huggingface_vit: Tuple[HuggingFaceModel, TorchData],
    api_storage_client: client.StorageClient,
) -> None:
    """An example of saving a large, pretrained  vit model to opsml"""
    model, data = huggingface_vit

    datacard = DataCard(
        interface=data,
        name="vit",
        repository="mlops",
        contact="test@mlops.com",
    )
    api_registries.data.register_card(datacard)

    modelcard = ModelCard(
        interface=model,
        name="vit",
        repository="mlops",
        contact="test@mlops.com",
        tags={"id": "model1"},
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    api_registries.model.register_card(modelcard)

    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(model.model_suffix))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.FEATURE_EXTRACTOR.value).with_suffix(""))


@mock.patch("opsml.storage.scouter.ScouterClient.request")
def test_model_registry_scouter(
    mock_request: mock.MagicMock,
    linear_regression: Tuple[SklearnModel, NumpyData],
    api_registries: CardRegistries,
) -> None:
    mock_request.return_value = None

    data_registry = api_registries.data
    model_registry = api_registries.model
    model, data = linear_regression

    datacard = DataCard(
        interface=data,
        name="scouter_test",
        repository="mlops",
        contact="mlops.com",
    )

    data_registry.register_card(card=datacard)

    drift_config = DriftConfig()
    model.create_drift_profile(data.data, drift_config)

    modelcard = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    model_registry.register_card(card=modelcard)

    assert modelcard.interface.drift_profile is not None
    assert modelcard.interface.drift_profile.config.name == modelcard.name
    assert mock_request.called


@mock.patch("opsml.storage.scouter.ScouterClient.request")
def test_get_profile_success(mock_request: mock.MagicMock, test_app: TestClient) -> None:
    mock_request.return_value = {"status": "success", "profile": {"name": "model"}}
    response = test_app.get(
        "/opsml/drift/profile",
        params={"repository": "mlops", "name": "model", "version": "0.1.0"},
    )

    assert response.status_code == 200
    assert response.json()["profile"]["name"] == "model"
    assert mock_request.called


@mock.patch("opsml.storage.scouter.ScouterClient.request")
def test_get_profile_error(mock_request: mock.MagicMock, test_app: TestClient) -> None:
    mock_request.return_value = {"status": "error"}
    response = test_app.get(
        "/opsml/drift/profile",
        params={"repository": "mlops", "name": "model", "version": "0.1.0"},
    )

    assert response.status_code == 200
    assert response.json()["profile"] is None
    assert mock_request.called


@mock.patch("opsml.storage.scouter.ScouterClient.request")
def test_get_drift_values(mock_request: mock.MagicMock, test_app: TestClient) -> None:
    mock_request.return_value = {
        "data": {
            "features": {
                "col_1": {
                    "created_at": [
                        "2024-09-18T06:43:12",
                    ],
                    "values": [
                        -0.8606220085107592,
                    ],
                },
            }
        },
        "status": "success",
    }
    response = test_app.get(
        "/opsml/drift/values",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "time_window": "2day",
            "max_data_points": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["features"]["col_1"]["values"][0] == -0.8606220085107592
    assert mock_request.called

    response = test_app.get(
        "/opsml/drift/values",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "time_window": "2day",
            "max_data_points": 10,
            "feature": "col_1",
        },
    )

    assert response.status_code == 200
    assert mock_request.called
