from typing import Dict, List
import pandas as pd
from ydata_profiling import ProfileReport
from numpy.typing import NDArray
import pyarrow as pa
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.sql.registry import CardRegistry
from opsml.registry import DataCard


def test_datacard_create_data_profile(
    db_registries: Dict[str, CardRegistry],
    iris_data: pd.DataFrame,
):
    # create data card
    registry = db_registries["data"]
    data_card = DataCard(
        data=iris_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    data_card.create_data_profile()
    registry.register_card(data_card)

    assert data_card.uris.profile_uri is not None


def test_feed_data_profile(
    db_registries: Dict[str, CardRegistry],
    iris_data: pd.DataFrame,
):
    # create data card
    registry = db_registries["data"]

    profile = ProfileReport(iris_data, title="Profiling Report")
    data_card = DataCard(
        data=iris_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_profile=profile,
    )
