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


def test_upload_fail(
    test_app: TestClient,
):
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

    print(response.__dict__)
    a
