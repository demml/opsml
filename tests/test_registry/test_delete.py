from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import polars as pl
from numpy.typing import NDArray
import pyarrow as pa
from os import path
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
)
from opsml.registry.sql.registry import CardRegistry
from opsml.helpers.exceptions import VersionError
from sklearn import linear_model
from sklearn.pipeline import Pipeline
import uuid
from pydantic import ValidationError
from tests.conftest import FOURTEEN_DAYS_TS, FOURTEEN_DAYS_STR


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
    ],
)
def test_delete_card(
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

    cards = registry.list_cards(name="test_df", team="mlops")
    assert len(cards) == 1
    filepath = data_card.metadata.uris.data_uri

    # delete data card
    registry.delete_card(card=data_card)
    cards = registry.list_cards(name="test_df", team="mlops")

    # check registry record is deleted
    assert len(cards) == 0

    # check data is deleted
    assert not path.exists(filepath)
