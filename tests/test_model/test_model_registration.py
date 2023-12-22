import pathlib
import re
import sys
import uuid
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastapi.exceptions import HTTPException
from numpy.typing import NDArray
from pydantic import ValidationError
from pytest_lazyfixture import lazy_fixture
from requests.auth import HTTPBasicAuth
from sklearn import linear_model, pipeline
from starlette.testclient import TestClient

from opsml.app.routes.files import verify_path
from opsml.app.routes.pydantic_models import AuditFormRequest, CommentSaveRequest
from opsml.app.routes.utils import error_to_500, list_team_name_info
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import (
    AuditCard,
    CardInfo,
    CardRegistries,
    CardRegistry,
    DataCard,
    DataCardMetadata,
    ModelCard,
    ModelCardMetadata,
    PipelineCard,
    RunCard,
)
from opsml.registry.sql.registry import CardRegistries
from opsml.registry.storage.api import ApiRoutes
from opsml.settings.config import config
from tests.conftest import TODAY_YMD

EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)


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
    registry.register_card(card=data_card)
