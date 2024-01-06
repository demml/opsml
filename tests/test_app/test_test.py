import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple, cast
from unittest.mock import MagicMock, patch
import pdb
import pandas as pd
import pytest
from fastapi.exceptions import HTTPException
from numpy.typing import NDArray
from requests.auth import HTTPBasicAuth
from sklearn import pipeline
from starlette.testclient import TestClient

from opsml.app.core.dependencies import swap_opsml_root
from opsml.app.routes.pydantic_models import AuditFormRequest, CommentSaveRequest
from opsml.app.routes.utils import error_to_500, list_team_name_info
from opsml.cards import (
    AuditCard,
    CardInfo,
    DataCard,
    DataCardMetadata,
    ModelCard,
    ModelCardMetadata,
    PipelineCard,
    RunCard,
)
from opsml.data import NumpyData, PandasData
from opsml.model import SklearnModel
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import CardRegistries, CardRegistry
from opsml.settings.config import config
from opsml.storage import client
from opsml.storage.api import ApiRoutes
from opsml.types import SaveName
from opsml.types.extra import Suffix
from tests.conftest import TODAY_YMD

EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)



def test_metadata_download_and_registration(
    test_app: TestClient,
    api_registries: CardRegistries,
    linear_regression: Tuple[SklearnModel, NumpyData],
):
    team = "mlops"
    user_email = "test@mlops.com"

    model, data = linear_regression

    data_registry = api_registries.data
    model_registry = api_registries.model

    data_card = DataCard(
        interface=data,
        name="test_data",
        team=team,
        user_email=user_email,
    )

    data_registry.register_card(card=data_card)

    model_card = ModelCard(
        interface=model,
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
    assert re.search(rf"model_registry/test-model/v{model_card.version}$", uri, re.IGNORECASE) is not None

    download_path = (model_card.uri / SaveName.TRAINED_MODEL.value).with_suffix(model.model_suffix)
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
    assert re.search(rf"model_registry/test-model/v{model_card.version}$", uri, re.IGNORECASE) is not None

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
    assert re.search(rf"model_registry/test-model/v{minor}$", uri, re.IGNORECASE) is not None

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
    assert re.search(rf"model_registry/test-model/v{major}$", uri, re.IGNORECASE) is not None

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

