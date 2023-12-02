from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import polars as pl
from numpy.typing import NDArray
import pyarrow as pa
from os import path
from sqlalchemy import select
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.cards import (
    DataCard,
    RunCard,
    PipelineCard,
    ModelCard,
    DataSplit,
    DataCardMetadata,
    ModelCardMetadata,
    Description,
    CardInfo,
    Description,
)
from opsml.registry.sql.registry import CardRegistry
from opsml.registry.sql.sql_schema import DataSchema
from opsml.registry.sql.base.query_engine import DialectHelper
from opsml.helpers.exceptions import VersionError
from sklearn import linear_model
from sklearn.pipeline import Pipeline
import uuid
from pydantic import ValidationError
from tests.conftest import FOURTEEN_DAYS_TS, FOURTEEN_DAYS_STR


def test_registry_dialect(
    db_registries: Dict[str, CardRegistry],
    tracking_uri: str,
):
    registry = db_registries["data"]

    if "postgres" in tracking_uri:
        assert "postgres" in registry._registry.engine.dialect

    elif "mysql" in tracking_uri:
        assert "mysql" in registry._registry.engine.dialect

    elif "sqlite" in tracking_uri:
        assert "sqlite" in registry._registry.engine.dialect
    else:
        raise ValueError("Supported dialect not found")


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_arrow_table")),
        (lazy_fixture("test_polars_split"), lazy_fixture("test_polars_dataframe")),
    ],
)
def test_register_data(
    db_registries: Dict[str, CardRegistry],
    test_data: tuple[pd.DataFrame, NDArray, pa.Table],
    data_splits: List[Dict[str, str]],
):
    # create data card
    registry = db_registries["data"]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )

    registry.register_card(card=data_card)

    # test idempotency
    version = data_card.version
    registry.register_card(card=data_card)
    assert data_card.version == version

    df = registry.list_cards(name=data_card.name, team=data_card.team, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(name=data_card.name, as_dataframe=True)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(as_dataframe=True)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(name=data_card.name, team=data_card.team, version="1.0.0", as_dataframe=True)
    assert df.shape[0] == 1

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )
    registry.register_card(card=data_card)

    cards = registry.list_cards(
        name=data_card.name,
        team=data_card.team,
        version="^1",
        as_dataframe=False,
    )
    assert len(cards) >= 1

    # Verify card name normalization (replacing "_" with "-")
    names = registry._registry.get_unique_card_names(team="mlops")
    # NOTE: opsml replaces "_" with "-" in card name name
    assert "test-df" in names

    names = registry._registry.get_unique_card_names()
    assert "test-df" in names

    assert "mlops" in registry._registry.unique_teams
