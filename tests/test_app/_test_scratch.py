from typing import Dict, List, Tuple

import re
import uuid

import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture
from starlette.testclient import TestClient
from sklearn import linear_model, pipeline
from numpy.typing import NDArray
from pydantic import ValidationError
from requests.auth import HTTPBasicAuth

from opsml.registry import DataCard, ModelCard, RunCard, PipelineCard, CardRegistry, CardRegistries, CardInfo
from opsml.helpers.request_helpers import ApiRoutes
from opsml.app.core import config
from tests.conftest import TODAY_YMD
from unittest.mock import patch, MagicMock


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
