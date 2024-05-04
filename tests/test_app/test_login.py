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
from opsml.types import Metric, SaveName
from opsml.types.extra import Suffix
from tests.conftest import TODAY_YMD

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_app_with_login(test_app_login: TestClient) -> None:
    """Test healthcheck with login"""

    response = test_app_login.get(
        "/opsml/healthcheck"
    )

    assert response.status_code == 200