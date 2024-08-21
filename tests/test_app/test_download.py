import re
import shutil
from typing import Tuple
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from opsml.cards import AuditCard, DataCard, ModelCard
from opsml.settings.config import config
from opsml.storage.api import ApiRoutes
from opsml.types import SaveName


def test_metadata_download_and_registration(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:
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
        json={
            "name": model_card.name,
            "repository": model_card.repository,
            "version": model_card.version,
        },
    )
    # NOTE: the *exact* model version sent must be returned in the URL.
    # Otherwise the hosting infrastructure will not know where to find the URL
    # as they do *not* use the response text, rather they assume the URL is in
    # the correct format.
    uri = response.json()
    assert (
        re.search(
            rf"{config.opsml_registry_path}/{model_card.repository}/{model_card.name}/v{model_card.version}$",
            uri,
            re.IGNORECASE,
        )
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
            "repository": model_card.repository,
            "version": model_card.version,
            "onnx": "false",
        },
    )
    uri = response.json()
    assert (
        re.search(
            rf"{config.opsml_registry_path}/{model_card.repository}/{model_card.name}/v{model_card.version}$",
            uri,
            re.IGNORECASE,
        )
        is not None
    )

    # test register model - latest patch given latest major.minor
    minor = model_card.version[0 : model_card.version.rindex(".")]
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": model_card.name,
            "repository": model_card.repository,
            "version": minor,
        },
    )

    uri = response.json()
    assert (
        re.search(
            rf"{config.opsml_registry_path}/{model_card.repository}/{model_card.name}/v{minor}$", uri, re.IGNORECASE
        )
        is not None
    )

    # test register model - latest minor / patch given major only
    major = model_card.version[0 : model_card.version.index(".")]
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": model_card.name,
            "repository": model_card.repository,
            "version": major,
        },
    )
    uri = response.json()
    assert (
        re.search(
            rf"{config.opsml_registry_path}/{model_card.repository}/{model_card.name}/v{major}$", uri, re.IGNORECASE
        )
        is not None
    )

    # test version fail - invalid name
    response = test_app.post(
        url=f"opsml/{ApiRoutes.REGISTER_MODEL}",
        json={
            "name": "non-exist",
            "repository": "non-exist",
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
            "repository": "non-exist",
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
                "repository": model_card.repository,
                "version": model_card.version,
            },
        )

        msg = response.json()["detail"]
        assert response.status_code == 500

    shutil.rmtree(config.opsml_registry_path, ignore_errors=True)

    response = test_app.post(
        url=f"/opsml/{ApiRoutes.METRICS}",
        json={"run_uid": model_card.metadata.runcard_uid},
    )
    assert response.status_code == 200

    response = test_app.get(url=f"opsml/files/download/ui?path={model_card.uri}/{SaveName.TRAINED_MODEL.value}")
    assert response.status_code == 200
