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
