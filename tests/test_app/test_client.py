from typing import Dict, List, Tuple
import re
import uuid
import pathlib
import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture
from starlette.testclient import TestClient
from sklearn import linear_model, pipeline
from numpy.typing import NDArray
from pydantic import ValidationError
from requests.auth import HTTPBasicAuth
from opsml.registry import (
    AuditCard,
    DataCard,
    ModelCard,
    RunCard,
    PipelineCard,
    CardRegistry,
    CardRegistries,
    CardInfo,
    DataCardMetadata,
    ModelCardMetadata,
)
from opsml.app.routes.utils import list_team_name_info, error_to_500
from opsml.app.routes.pydantic_models import AuditFormRequest, CommentSaveRequest
from opsml.helpers.request_helpers import ApiRoutes
from opsml.projects import OpsmlProject
from opsml.app.core import config
from tests.conftest import TODAY_YMD
from unittest.mock import patch, MagicMock


def test_app_settings(test_app: TestClient):
    """Test settings"""

    response = test_app.get(f"/opsml/{ApiRoutes.SETTINGS}")

    assert response.status_code == 200
    assert response.json()["proxy"] is True


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


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
    ],
)
def test_register_data(
    api_registries: CardRegistries,
    test_data: Tuple[pd.DataFrame, NDArray],
    data_splits: List[Dict[str, str]],
):
    # create data card
    registry = api_registries.data

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )
    data_card.create_data_profile()
    registry.register_card(card=data_card)

    df = registry.list_cards(name=data_card.name, team=data_card.team, max_date=TODAY_YMD, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(name=data_card.name, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(as_dataframe=True)
    assert isinstance(df, pd.DataFrame)


def test_list_teams(
    api_registries: CardRegistries,
):
    registry: CardRegistry = api_registries.data
    teams = registry._registry.unique_teams
    assert len(teams) == 1
    assert teams[0] == "mlops"


def test_list_card_names(
    api_registries: CardRegistries,
):
    # create data card
    registry = api_registries.data
    names = registry._registry.get_unique_card_names(team="mlops")

    assert len(names) == 1
    assert names[0] == "test-df"

    names = registry._registry.get_unique_card_names()

    assert len(names) == 1
    assert names[0] == "test-df"


def test_list_team_info(
    api_registries: CardRegistries,
):
    registry = api_registries.data
    info = list_team_name_info(registry=registry, team="mlops")
    assert info.names[0] == "test-df"
    assert info.teams[0] == "mlops"

    info = list_team_name_info(registry=registry)
    assert info.names[0] == "test-df"


def test_register_major_minor(api_registries: CardRegistries, test_array: NDArray):
    # create data card
    registry = api_registries.data

    data_card = DataCard(
        data=test_array,
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.1.1",
    )

    registry.register_card(card=data_card)

    data_card = DataCard(
        data=test_array,
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.1",
    )

    registry.register_card(card=data_card, version_type="patch")
    assert data_card.version == "3.1.2"

    data_card = DataCard(
        data=test_array,
        name="major_minor",
        team="mlops",
        user_email="mlops.com",
        version="3.1",
    )

    registry.register_card(card=data_card, version_type="minor")
    assert data_card.version == "3.2.0"


def test_semver_registry_list(api_registries: CardRegistries, test_array: NDArray):
    # create data card
    registry = api_registries.data

    data_card = DataCard(
        data=test_array,
        name="test_array",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)

    # version 2
    data_card = DataCard(
        data=test_array,
        name="test_array",
        team="mlops",
        user_email="mlops.com",
    )
    registry.register_card(card=data_card, version_type="major")

    for i in range(0, 12):
        data_card = DataCard(
            data=test_array,
            name="test_array",
            team="mlops",
            user_email="mlops.com",
        )
        registry.register_card(card=data_card)

    # should return 13 versions
    cards = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="2.*.*",
    )
    assert len(cards) == 13

    cards = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="^2.3.0",
    )
    assert len(cards) == 1

    cards = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="~2.3.0",
    )
    assert len(cards) == 1


def test_run_card(
    linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame],
    api_registries: CardRegistries,
):
    registry = api_registries.run

    run = RunCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        datacard_uids=["test_uid"],
    )
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10
    assert run.get_metric("test_metric2").value == 20
    # save artifacts
    model, _ = linear_regression
    run.log_artifact("reg_model", artifact=model)
    assert run.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"
    registry.register_card(card=run)

    loaded_card = registry.load_card(uid=run.uid)
    assert loaded_card.uid == run.uid


def test_register_model(
    api_registries: CardRegistries,
    sklearn_pipeline: Tuple[pipeline.Pipeline, pd.DataFrame],
):
    model, data = sklearn_pipeline
    # create data card
    data_registry = api_registries.data

    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)

    model_card1 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry = api_registries.model
    model_registry.register_card(model_card1)

    loaded_card = model_registry.load_card(uid=model_card1.uid)
    loaded_card.load_trained_model()
    loaded_card.trained_model = model
    loaded_card.sample_input_data = data[0:1]

    assert getattr(loaded_card, "trained_model") is not None
    assert getattr(loaded_card, "sample_input_data") is not None

    model_card_custom = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry.register_card(card=model_card_custom)
    assert "pipeline-model" in model_card_custom.metadata.uris.trained_model_uri

    model_card2 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=None,
        to_onnx=True,
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card2)

    model_card3 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid="test_uid",
        to_onnx=True,
    )

    with pytest.raises(ValueError):
        model_registry.register_card(card=model_card3)

    with pytest.raises(ValidationError):
        model_card3 = ModelCard(
            trained_model=model,
            sample_input_data=None,
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            datacard_uid="test_uid",
            to_onnx=True,
        )

    # test card tags
    cards = model_registry.list_cards(
        name=model_card1.name,
        team=model_card1.team,
        tags=model_card1.tags,
    )

    assert cards[0]["tags"] == {"id": "model1"}

    # try registering model to different team
    model_card_dup = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="new-team",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )
    with pytest.raises(ValueError) as ve:
        model_registry.register_card(card=model_card_dup)
    assert ve.match("Failed to set version. Model name already exists for a different team")


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_load_data_card(api_registries: CardRegistries, test_data: pd.DataFrame):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry = api_registries.data

    data_split = [
        {"label": "train", "column_name": "year", "column_value": 2020},
        {"label": "test", "column_name": "year", "column_value": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        name=data_name,
        team=team,
        user_email=user_email,
        data_splits=data_split,
        metadata=DataCardMetadata(additional_info={"input_metadata": 20}),
        dependent_vars=[200, "test"],
    )

    data_card.add_info(info={"added_metadata": 10})
    registry.register_card(card=data_card)
    loaded_data: DataCard = registry.load_card(name=data_name, version=data_card.version)

    loaded_data.load_data()

    assert int(loaded_data.metadata.additional_info["input_metadata"]) == 20
    assert int(loaded_data.metadata.additional_info["added_metadata"]) == 10
    assert isinstance(loaded_data.dependent_vars[0], int)
    assert isinstance(loaded_data.dependent_vars[1], str)
    assert bool(loaded_data)

    # update
    loaded_data.version = "1.2.0"
    registry.update_card(card=loaded_data)

    record = registry.query_value_from_card(uid=loaded_data.uid, columns=["version", "timestamp"])
    assert record["version"] == "1.2.0"

    # test assertion error
    with pytest.raises(ValueError):
        data_card = DataCard(
            name=data_name,
            team=team,
            user_email=user_email,
            data_splits=data_split,
            metadata=DataCardMetadata(additional_info={"input_metadata": 20}),
            dependent_vars=[200, "test"],
        )

    # load card again
    datacardv12: DataCard = registry.load_card(name=data_name, version="1.2.0")
    datacardv12.metadata.uris.data_uri = "fail"

    with pytest.raises(Exception):
        datacardv12.load_data()


def test_pipeline_registry(api_registries: CardRegistry):
    pipeline_card = PipelineCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
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
    api_registries: CardRegistries,
    linear_regression: Tuple[linear_model.LinearRegression, pd.DataFrame],
):
    team = "mlops"
    user_email = "test@mlops.com"

    model, data = linear_regression

    data_registry = api_registries.data
    model_registry = api_registries.model

    data_card = DataCard(
        data=data,
        name="test_data",
        team=team,
        user_email=user_email,
    )

    data_registry.register_card(card=data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[:1],
        name="test_model",
        team=team,
        user_email=user_email,
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry.register_card(model_card)

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
    assert re.search(rf"/model_registry/test-model/v{model_card.version}$", uri, re.IGNORECASE) is not None

    response = test_app.get(
        url=f"opsml/{ApiRoutes.DOWNLOAD_FILE}?read_path={model_card.metadata.uris.trained_model_uri}",
    )

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
    assert re.search(rf"/model_registry/test-model/v{model_card.version}$", uri, re.IGNORECASE) is not None

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
    assert re.search(rf"/model_registry/test-model/v{minor}$", uri, re.IGNORECASE) is not None

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
    assert re.search(rf"/model_registry/test-model/v{major}$", uri, re.IGNORECASE) is not None

    # test version fail - invalid name
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": "non-exist",
            "version": model_card.version,
        },
    )

    msg = response.json()["detail"]
    assert response.status_code == 404
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
        "opsml.registry.model.registrar.ModelRegistrar.is_registered",
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


def test_download_model_metadata_failure(test_app: TestClient):
    response = test_app.post(url=f"opsml/{ApiRoutes.MODEL_METADATA}", json={"name": "pip"})

    # should fail
    assert response.status_code == 404
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
    api_registries: CardRegistries,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    model, data = sklearn_pipeline
    card_info = CardInfo(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
    )

    runcard = RunCard(info=card_info)

    runcard.log_metric(key="m1", value=1.1)
    runcard.log_metric(key="mape", value=2, step=1)
    runcard.log_metric(key="mape", value=2, step=2)
    runcard.log_parameter(key="m1", value="apple")
    api_registries.run.register_card(runcard)

    #### Create DataCard
    datacard = DataCard(
        data=data,
        name="profile_data",
        team="mlops",
        user_email="mlops.com",
    )
    datacard.create_data_profile()
    api_registries.data.register_card(datacard)

    #### Create ModelCard
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=card_info,
        datacard_uid=datacard.uid,
        metadata=ModelCardMetadata(runcard_uid=runcard.uid),
        to_onnx=True,
    )
    api_registries.model.register_card(modelcard)

    auditcard = AuditCard(name="audit_card", team="team", user_email="test")
    auditcard.add_card(card=modelcard)
    api_registries.audit.register_card(auditcard)

    ### create second ModelCard
    #### Create ModelCard
    modelcard_2 = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=card_info,
        datacard_uid=datacard.uid,
        metadata=ModelCardMetadata(runcard_uid=runcard.uid),
        to_onnx=True,
    )
    api_registries.model.register_card(modelcard_2)

    response = test_app.post(url=f"/opsml/{ApiRoutes.MODEL_METRICS}", json={"uid": modelcard.uid})

    metrics = response.json()

    assert metrics["metrics"]["m1"][0]["value"] == 1.1

    response = test_app.post(
        url=f"/opsml/{ApiRoutes.MODEL_METRICS}",
        json={
            "name": modelcard.name,
            "team": modelcard.team,
        },
    )

    assert response.status_code == 500

    comment = CommentSaveRequest(
        uid=auditcard.uid,
        name=auditcard.name,
        team=auditcard.team,
        email=auditcard.user_email,
        selected_model_name=modelcard.name,
        selected_model_version=modelcard.version,
        selected_model_team=modelcard.team,
        selected_model_email=modelcard.user_email,
        comment_name="test",
        comment_text="test",
    )

    # test auditcard comment
    response = test_app.post(
        "/opsml/audit/comment/save",
        data=comment.model_dump(),
    )
    assert response.status_code == 200


def test_model_metric_failure(
    test_app: TestClient,
    api_registries: CardRegistries,
    sklearn_pipeline: Tuple[pipeline.Pipeline, pd.DataFrame],
):
    model, data = sklearn_pipeline
    card_info = CardInfo(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
    )

    #### Create DataCard
    datacard = DataCard(data=data, info=card_info)
    api_registries.data.register_card(datacard)

    #### Create ModelCard
    modelcard = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        info=card_info,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )
    api_registries.model.register_card(modelcard)

    response = test_app.post(url=f"/opsml/{ApiRoutes.MODEL_METRICS}", json={"uid": modelcard.uid})
    assert response.status_code == 500


def test_token_fail(
    api_registries: CardRegistries,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(config.config, "APP_ENV", "production")
    monkeypatch.setattr(config.config, "PROD_TOKEN", "fail")

    run = RunCard(
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        datacard_uids=["test_uid"],
    )

    with pytest.raises(
        ValueError,
        match="Cannot perform write operation on prod resource without token",
    ):
        api_registries.run.register_card(card=run)


def test_delete_fail(test_app: TestClient):
    """Test error path"""

    pathlib.Path("tests/assets/empty/model_registry").mkdir(parents=True, exist_ok=True)

    response = test_app.post("/opsml/files/delete", json={"read_path": "tests/assets/empty/model_registry"})

    assert response.status_code == 200

    # this should fail because there is no file
    response = test_app.post("/opsml/files/delete", json={"read_path": "fail"})
    assert response.status_code == 422


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
    api_registries: CardRegistries,
    opsml_project: OpsmlProject,
    sklearn_pipeline: tuple[pipeline.Pipeline, pd.DataFrame],
):
    """Test settings"""

    model, data = sklearn_pipeline

    with opsml_project.run() as run:
        datacard = DataCard(
            data=data,
            name="test_data",
            team="mlops",
            user_email="mlops.com",
        )
        datacard.create_data_profile()
        run.register_card(card=datacard)
        run.log_metric("test_metric", 10)
        run.log_metrics({"test_metric2": 20})

        modelcard = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            tags={"id": "model1"},
            datacard_uid=datacard.uid,
            to_onnx=True,
        )
        run.register_card(modelcard)

    response = test_app.get("/opsml/data/versions/")
    assert response.status_code == 200

    response = test_app.get("/opsml/data/versions/?name=test_data")
    assert response.status_code == 200

    response = test_app.get("/opsml/data/versions/?name=test_data&version=1.0.0&load_profile=true")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/data/versions/uid/?uid={datacard.uid}")
    assert response.status_code == 200

    response = test_app.get(
        "/opsml/data/profile/view/?name=test_data&version=1.0.0&profile_uri=tests/assets/data_profile.html"
    )
    assert response.status_code == 200

    response = test_app.get("/opsml/models/versions/")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/models/versions/?model={modelcard.name}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/models/versions/?model={modelcard.name}&version={modelcard.version}")
    assert response.status_code == 200

    response = test_app.get("/opsml/projects/list/?project=test:test-exp")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/projects/list/?project=test:test-exp&run_uid={run.runcard.uid}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/projects/runs/plot/?run_uid={run.runcard.uid}")
    assert response.status_code == 200


##### Test audit
def test_audit(test_app: TestClient):
    """Test settings"""

    response = test_app.get("/opsml/audit/")
    assert response.status_code == 200

    response = test_app.get("/opsml/audit/?team=mlops")
    assert response.status_code == 200

    response = test_app.get("/opsml/audit/?team=mlops&?model=pipeline_model")
    assert response.status_code == 200

    response = test_app.get("/opsml/audit/?team=mlops&model=pipeline_model&version=1.0.0")
    assert response.status_code == 200

    audit_form = AuditFormRequest(
        selected_model_name="pipeline_model",
        selected_model_team="mlops",
        selected_model_version="1.0.0",
        selected_model_email="mlops.com",
        name="pipeline_audit",
        team="mlops",
        email="mlops.com",
    )

    response = test_app.post(
        "/opsml/audit/save",
        data=audit_form.model_dump(),
    )

    assert response.status_code == 200


def test_error_wrapper():
    @error_to_500
    async def fail(request):
        raise ValueError("Fail")

    fail("fail")


def test_audit_upload(
    test_app: TestClient,
    api_registries: CardRegistries,
    sklearn_pipeline: Tuple[pipeline.Pipeline, pd.DataFrame],
):
    model, data = sklearn_pipeline

    #### Create DataCard
    datacard = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    api_registries.data.register_card(datacard)

    #### Create ModelCard
    modelcard = ModelCard(
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        trained_model=model,
        sample_input_data=data[0:1],
        datacard_uid=datacard.uid,
        to_onnx=True,
    )
    api_registries.model.register_card(modelcard)

    file_ = "tests/assets/audit_file.csv"

    audit_form = AuditFormRequest(
        name="pipeline_audit",
        team="mlops",
        email="mlops.com",
        selected_model_name="pipeline_model",
        selected_model_team="mlops",
        selected_model_version="1.0.0",
        selected_model_email="mlops.com",
    )

    # save audit card
    response = test_app.post(
        "/opsml/audit/save",
        data=audit_form.model_dump(),
    )
    auditcard = api_registries.audit.list_cards()[0]

    # without uid
    response = test_app.post(
        "/opsml/audit/upload",
        data=audit_form.model_dump(),
        files={"audit_file": open(file_, "rb")},
    )
    assert response.status_code == 200

    # with uid

    audit_form = AuditFormRequest(
        name="pipeline_audit",
        team="mlops",
        email="mlops.com",
        selected_model_name="pipeline_model",
        selected_model_team="mlops",
        selected_model_version="1.0.0",
        selected_model_email="mlops.com",
        uid=auditcard["uid"],
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
        url=f"opsml/{ApiRoutes.UPLOAD}",
        files=files,
        headers=headers,
    )

    assert response.status_code == 422


def test_download_fail(test_app: TestClient):
    # test register model (onnx)
    response = test_app.get(url=f"opsml/{ApiRoutes.DOWNLOAD_FILE}?read_path=fake")
    assert response.status_code == 422
