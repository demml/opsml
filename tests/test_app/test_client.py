import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple, cast
from unittest.mock import MagicMock, patch

import pytest
from requests.auth import HTTPBasicAuth
from starlette.testclient import TestClient

from opsml.app.routes.pydantic_models import AuditFormRequest, CommentSaveRequest
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
from opsml.projects.active_run import ActiveRun
from opsml.registry import CardRegistries, CardRegistry
from opsml.settings.config import config
from opsml.storage import client
from opsml.storage.api import ApiRoutes
from opsml.types import SaveName
from opsml.types.extra import Suffix
from tests.conftest import TODAY_YMD

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_debug(test_app: TestClient):
    """Test debug path"""

    response = test_app.get("/opsml/debug")

    assert "tmp.db" in response.json()["url"]
    assert "mlruns" in response.json()["storage"]
    assert response.status_code == 200


def test_error(test_app: TestClient):
    """Test error path"""

    response = test_app.get("/opsml/error")

    assert response.status_code == 500


def test_register_data(
    api_registries: CardRegistries, api_storage_client: client.StorageClient, pandas_data: PandasData
):
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

    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    _ = registry.list_cards(name=datacard.name, repository=datacard.repository, max_date=TODAY_YMD)

    _ = registry.list_cards(name=datacard.name)

    _ = registry.list_cards()

    # Verify repositories / names
    repositories = registry._registry.unique_repositories
    assert "mlops" in repositories

    names = registry._registry.get_unique_card_names(repository="mlops")
    assert "test-df" in names

    info = list_repository_name_info(registry=registry, repository="mlops")
    assert "mlops" in info.repositories
    assert "test-df" in info.names

    info = list_repository_name_info(registry=registry)
    assert "mlops" in info.repositories
    assert "test-df" in info.names


def test_register_major_minor(api_registries: CardRegistries, numpy_data: NumpyData):
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


def test_semver_registry_list(api_registries: CardRegistries, numpy_data: NumpyData):
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


def test_run_card(
    linear_regression: Tuple[SklearnModel, NumpyData],
    api_registries: CardRegistries,
    api_storage_client: client.StorageClient,
):
    registry = api_registries.run
    model, data = linear_regression

    run = RunCard(name="run", contact="mlops.com", datacard_uids=["test_uid"])
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10
    assert run.get_metric("test_metric2").value == 20

    # save artifacts
    run.log_artifact_from_file(name="cats", local_path="tests/assets/cats.jpg")
    assert api_storage_client.exists(Path(run.artifact_uris["cats"].remote_path))
    registry.register_card(card=run)

    # Load the card and verify artifacts / metrics
    loaded_card: RunCard = registry.load_card(uid=run.uid)
    assert loaded_card.uid == run.uid
    assert loaded_card.get_metric("test_metric").value == 10
    assert loaded_card.get_metric("test_metric2").value == 20
    loaded_card.load_artifacts()


def test_register_model_data(
    api_registries: CardRegistries,
    populate_model_data_for_api: Tuple[ModelCard, DataCard],
    api_storage_client: client.StorageClient,
):
    model_registry = api_registries.model
    data_registry = api_registries.data
    modelcard, datacard = populate_model_data_for_api

    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(".joblib"))
    assert api_storage_client.exists(
        Path(datacard.uri, SaveName.DATA.value).with_suffix(datacard.interface.data_suffix)
    )

    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))

    loaded_card: ModelCard = model_registry.load_card(uid=modelcard.uid)
    loaded_card.load_model()
    assert loaded_card.model is not None
    assert loaded_card.sample_data is not None

    with pytest.raises(ValueError):
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

    with pytest.raises(ValueError) as ve:
        # try registering model to different repository
        model_card_dup = ModelCard(
            interface=modelcard.interface,
            name=modelcard.name,
            repository="new-repository",
            contact="mlops.com",
            datacard_uid=datacard.uid,
            to_onnx=True,
        )
        model_registry.register_card(card=model_card_dup)
    assert ve.match("different repository")

    # load data
    loaded_data: DataCard = data_registry.load_card(name=datacard.name, version=datacard.version)
    loaded_data.load_data()

    assert loaded_data.data is not None

    # update
    loaded_data.version = "1.2.0"
    data_registry.update_card(card=loaded_data)

    record = data_registry.query_value_from_card(uid=loaded_data.uid, columns=["version", "timestamp"])
    assert record["version"] == "1.2.0"

    # test assertion error
    with pytest.raises(ValueError):
        DataCard(
            name=datacard.name,
            repository=datacard.repository,
            contact=datacard.contact,
            metadata=DataCardMetadata(additional_info={"input_metadata": 20}),
        )


def test_pipeline_registry(api_registries: CardRegistry):
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


def test_metadata_download_and_registration(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
):
    model_card, _, _ = populate_model_data_for_route

    response = test_app.post(
        url=f"opsml/{ApiRoutes.MODEL_METADATA}",
        json={"uid": model_card.uid},
    )
    assert response.status_code == 200

    model_def = response.json()

    assert model_def["model_name"] == model_card.name
    assert model_def["model_version"] == model_card.version

    # test register model (onnx)
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={"name": model_card.name, "version": model_card.version},
    )
    # NOTE: the *exact* model version sent must be returned in the URL.
    # Otherwise the hosting infrastructure will not know where to find the URL
    # as they do *not* use the response text, rather they assume the URL is in
    # the correct format.
    uri = response.json()
    assert (
        re.search(rf"{config.opsml_registry_path}/{model_card.name}/v{model_card.version}$", uri, re.IGNORECASE)
        is not None
    )

    download_path = (model_card.uri / SaveName.TRAINED_MODEL.value).with_suffix(model_card.interface.model_suffix)
    response = test_app.get(url=f"opsml/{ApiRoutes.DOWNLOAD_FILE}?path={download_path}")

    assert response.status_code == 200

    # test register model (native)
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": model_card.name,
            "version": model_card.version,
            "onnx": "false",
        },
    )
    uri = response.json()
    assert (
        re.search(rf"{config.opsml_registry_path}/{model_card.name}/v{model_card.version}$", uri, re.IGNORECASE)
        is not None
    )

    # test register model - latest patch given latest major.minor
    minor = model_card.version[0 : model_card.version.rindex(".")]
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": model_card.name,
            "version": minor,
        },
    )

    uri = response.json()
    assert re.search(rf"{config.opsml_registry_path}/{model_card.name}/v{minor}$", uri, re.IGNORECASE) is not None

    # test register model - latest minor / patch given major only
    major = model_card.version[0 : model_card.version.index(".")]
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": model_card.name,
            "version": major,
        },
    )
    uri = response.json()
    assert re.search(rf"{config.opsml_registry_path}/{model_card.name}/v{major}$", uri, re.IGNORECASE) is not None

    # test version fail - invalid name
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": "non-exist",
            "version": model_card.version,
        },
    )

    msg = response.json()["detail"]
    assert response.status_code == 500
    assert "Model not found" == msg

    # test version fail (does not match regex)
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": "non-exist",
            "version": "v1.0.0",  # version should *not* contain "v" - it must match the n.n.n pattern
        },
    )

    loc = response.json()["detail"][0]["loc"]  # "location" of pydantic failure
    assert response.status_code == 422
    assert "version" in loc

    # test model copy failure. This should result in a 500 - internal server
    # error. The model exists and is valid, but the internal copy failed.
    # Returning a 4xx (i.e., 404) is not the correct response.
    with patch(
        "opsml.model.registrar.ModelRegistrar.is_registered",
        new_callable=MagicMock,
    ) as mock_registrar:
        mock_registrar.return_value = False
        response = test_app.post(
            url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
            json={
                "name": model_card.name,
                "version": model_card.version,
            },
        )

        msg = response.json()["detail"]
        assert response.status_code == 500

    shutil.rmtree(config.opsml_registry_path, ignore_errors=True)

    response = test_app.post(url=f"/opsml/{ApiRoutes.MODEL_METRICS}", json={"uid": model_card.uid})
    assert response.status_code == 200

    response = test_app.get(url=f"opsml/files/download/ui?path={model_card.uri}/{SaveName.TRAINED_MODEL.value}")
    assert response.status_code == 200


def test_download_model_metadata_failure(test_app: TestClient):
    response = test_app.post(url=f"opsml/{ApiRoutes.MODEL_METADATA}", json={"name": "pip"})

    # should fail
    assert response.status_code == 500
    assert response.json()["detail"] == "Model not found"


def test_app_with_login(test_app_login: TestClient):
    """Test healthcheck with login"""

    response = test_app_login.get(
        "/opsml/healthcheck",
        auth=HTTPBasicAuth("test-user", "test-pass"),
    )

    assert response.status_code == 200


def test_model_metrics(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    modelcard, _, _ = populate_model_data_for_route
    response = test_app.post(url=f"/opsml/{ApiRoutes.MODEL_METRICS}", json={"uid": modelcard.uid})

    metrics = response.json()

    assert metrics["metrics"]["m1"][0]["value"] == 1.1

    response = test_app.post(
        url=f"/opsml/{ApiRoutes.MODEL_METRICS}",
        json={
            "name": modelcard.name,
            "repository": modelcard.repository,
        },
    )
    assert response.status_code == 200


@pytest.mark.skipif(EXCLUDE, reason="Skipping")
def test_token_fail(
    monkeypatch: pytest.MonkeyPatch,
    api_registries: CardRegistries,
):
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


def test_delete_fail(test_app: TestClient):
    response = test_app.get("/opsml/files/delete", params={"path": "opsml-root:/OPSML_DATA_REGISTRY/notthere"})

    assert response.status_code == 200
    cast(Dict[str, Any], response.json())

    # Invaild path: does not include a registry table
    response = test_app.get("/opsml/files/delete", params={"path": "notthere"})
    assert response.status_code == 500


def test_card_create_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/create",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_update_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/update",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


def test_card_list_fail(test_app: TestClient):
    """Test error path"""

    response = test_app.post(
        "/opsml/cards/list",
        json={"card": {"blah": "blah"}, "registry_type": "blah"},
        headers={"X-Prod-Token": "test-token"},
    )

    assert response.status_code == 500


##### Test ui routes
def test_homepage(test_app: TestClient):
    """Test settings"""

    response = test_app.get("/opsml")
    assert response.status_code == 200


##### Test list models
def test_model_list(test_app: TestClient):
    """Test settings"""

    response = test_app.get("/opsml/models/list/")
    assert response.status_code == 200


##### Test list models
def test_data_list(test_app: TestClient):
    """Test settings"""
    response = test_app.get("/opsml/data/list/")
    assert response.status_code == 200


##### Test list data
def test_data_model_version(
    test_app: TestClient,
    populate_run: Tuple[DataCard, ModelCard, ActiveRun],
):
    """Test data routes"""

    datacard, modelcard, run = populate_run

    response = test_app.get("/opsml/data/versions/")
    assert response.status_code == 200

    response = test_app.get("/opsml/data/versions/?name=test_data")
    assert response.status_code == 200

    response = test_app.get("/opsml/data/versions/?name=test_data&version=1.0.0&load_profile=true")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/data/versions/uid/?uid={datacard.uid}")
    assert response.status_code == 200

    response = test_app.get("/opsml/models/versions/")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/models/versions/?model={modelcard.name}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/models/versions/?model={modelcard.name}&version={modelcard.version}")
    assert response.status_code == 200

    response = test_app.get("/opsml/projects/list/?project=opsml-project")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/projects/list/?project=opsml-project&run_uid={run.runcard.uid}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/projects/runs/plot/?run_uid={run.runcard.uid}")
    assert response.status_code == 200

    response = test_app.post(
        url="/opsml/models/compare_metrics",
        json={
            "metric_name": ["test_metric"],
            "lower_is_better": True,
            "challenger_uid": modelcard.uid,
            "champion_uid": [modelcard.uid],
        },
    )
    assert response.status_code == 200

    battle_report = response.json()
    assert battle_report["report"]["test_metric"][0]["challenger_win"] == False


##### Test audit
def test_audit(test_app: TestClient, populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard]):

    modelcard, datacard, auditcard = populate_model_data_for_route

    response = test_app.get("/opsml/audit/")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/audit/?repository={modelcard.repository}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/audit/?repository={modelcard.repository}&?model={modelcard.name}")
    assert response.status_code == 200

    audit_form = AuditFormRequest(
        selected_model_name=modelcard.name,
        selected_model_repository=modelcard.repository,
        selected_model_version=modelcard.version,
        selected_model_email=modelcard.contact,
        name="model_audit",
        repository="mlops",
        email="mlops.com",
    )

    response = test_app.post(
        "/opsml/audit/save",
        data=audit_form.model_dump(),
    )

    assert response.status_code == 200

    response = test_app.get(
        f"/opsml/audit/?repository={modelcard.repository}&model={modelcard.name}&version={modelcard.version}"
    )
    assert response.status_code == 200

    comment = CommentSaveRequest(
        uid=auditcard.uid,
        name=auditcard.name,
        repository=auditcard.repository,
        email=auditcard.contact,
        selected_model_name=modelcard.name,
        selected_model_version=modelcard.version,
        selected_model_repository=modelcard.repository,
        selected_model_email=modelcard.contact,
        comment_name="test",
        comment_text="test",
    )
    #
    ## test auditcard comment
    response = test_app.post(
        "/opsml/audit/comment/save",
        data=comment.model_dump(),
    )
    assert response.status_code == 200

    # upload
    # without uid
    file_ = "tests/assets/audit_file.csv"
    response = test_app.post(
        "/opsml/audit/upload",
        data=audit_form.model_dump(),
        files={"audit_file": open(file_, "rb")},
    )
    assert response.status_code == 200

    # with uid
    audit_form = AuditFormRequest(
        selected_model_name=modelcard.name,
        selected_model_repository=modelcard.repository,
        selected_model_version=modelcard.version,
        selected_model_email=modelcard.contact,
        name="model_audit",
        repository="mlops",
        email="mlops.com",
        uid=auditcard.uid,
    )

    response = test_app.post(
        "/opsml/audit/upload",
        data=audit_form.model_dump(),
        files={"audit_file": open(file_, "rb")},
    )
    assert response.status_code == 200

    # test downloading audit file
    response = test_app.post(
        "/opsml/audit/download",
        data=audit_form.model_dump(),
    )
    assert response.status_code == 200


def test_error_wrapper():
    @error_to_500
    async def fail(request):
        raise ValueError("Fail")

    fail("fail")


def test_registry_name_fail(test_app: TestClient):
    response = test_app.get(
        "/opsml/registry/table",
        params={"registry_type": "blah"},
    )

    assert response.status_code == 500


def test_upload_fail(test_app: TestClient):
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


def test_download_fail(test_app: TestClient):
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
