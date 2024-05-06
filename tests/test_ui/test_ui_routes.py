# test scripts to testing some ui routes
import sys
from typing import Tuple

from starlette.testclient import TestClient

from opsml.cards import AuditCard, DataCard, ModelCard

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_card_routes(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:
    """ify that we can read artifacts / metrics / cards without making a run
    active."""

    modelcard, _, _ = populate_model_data_for_route

    # test /card/registry/stats

    response = test_app.get(
        url="/opsml/cards/registry/stats",
        params={
            "registry_type": "model",
            "search_term": modelcard.repository,
        },
    )

    res = response.json()
    assert response.status_code == 200
    assert res == {"nbr_names": 1, "nbr_versions": 1, "nbr_repos": 1}

    # force error
    response = test_app.get(
        url="/opsml/cards/registry/stats",
        params={
            "registry_type": "error",
            "search_term": modelcard.repository,
        },
    )

    res = response.json()
    assert response.status_code == 500

    response = test_app.get(
        url="/opsml/cards/registry/query/page",
        params={
            "registry_type": "model",
            "search_term": modelcard.name,
            "repository": modelcard.repository,
        },
    )

    res = response.json()
    assert response.status_code == 200

    assert len(res["page"]) == 1

    # force error
    response = test_app.get(
        url="/opsml/cards/registry/query/page",
        params={
            "registry_type": "error",
            "search_term": modelcard.name,
            "repository": modelcard.repository,
        },
    )
    assert response.status_code == 500


def test_ui_datacard_route(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:

    modelcard, datacard, _ = populate_model_data_for_route

    # force error
    response = test_app.post(
        url="/opsml/data/card",
        json={
            "name": datacard.name,
            "repository": datacard.repository,
            "version": datacard.version,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == datacard.name


def test_ui_list_files(
    test_app: TestClient,
    populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard],
) -> None:

    modelcard, datacard, _ = populate_model_data_for_route

    # test info
    response = test_app.get(
        url="/opsml/files/list/info",
        params={
            "path": datacard.uri,
        },
    )

    assert response.status_code == 200
    assert response.json()["files"][0]["name"] == "data.zarr"

    # test modelcard
    response = test_app.get(
        url="/opsml/files/view",
        params={
            "path": f"{modelcard.uri}/model-metadata.json",
        },
    )

    assert response.status_code == 200
    assert response.json()["file_info"]["name"] == "model-metadata.json"

    response = test_app.get(
        url="/opsml/files/view",
        params={
            "path": f"{modelcard.uri}/trained-model.joblib",
        },
    )

    assert response.status_code == 200
    assert response.json()["file_info"]["name"] == "trained-model.joblib"

    # force error
    # test modelcard
    response = test_app.get(
        url="/opsml/files/view",
        params={
            "path": f"{modelcard.uri}/blah.json",
        },
    )

    assert response.status_code == 500

    # test readme
    response = test_app.post(
        url="/opsml/files/readme",
        json={
            "name": modelcard.name,
            "repository": modelcard.repository,
            "registry_type": "model",
            "content": "readme",
        },
    )

    assert response.status_code == 200

    response = test_app.post(
        url="/opsml/files/readme",
        json={
            "name": modelcard.name,
            "repository": "error",
            "registry_type": "model",
            "content": "readme",
        },
    )

    assert response.status_code == 200
    assert response.json() == False

    # error
    response = test_app.post(
        url="/opsml/files/readme",
        json={
            "name": modelcard.name,
            "repository": modelcard.repository,
            "registry_type": "error",
            "content": "readme",
        },
    )

    assert response.status_code == 200
    assert response.json() == False
