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
    )
    api_registries.model.register_card(modelcard)

    response = test_app.post(url=f"/opsml/{ApiRoutes.MODEL_METRICS}", json={"uid": modelcard.uid})

    print(response.json())
    assert response.status_code == 500
