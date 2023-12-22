import sys
from typing import Dict, List, Tuple

import pandas as pd
import pytest
from numpy.typing import NDArray
from pytest_lazyfixture import lazy_fixture

from opsml.registry import CardRegistries, DataCard
from opsml.registry.sql.registry import CardRegistries

EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
    ],
)
def _test_register_data(
    api_registries: CardRegistries,
    test_data: Tuple[pd.DataFrame, NDArray],
    data_splits: List[Dict[str, str]],
):
    # create data card
    registry = api_registries.data
    a

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )
    registry.register_card(card=data_card)

    registry.load_card(uid=data_card.uid)


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
    ],
)
def _test_register_data(
    db_registries: CardRegistries,
    test_data: Tuple[pd.DataFrame, NDArray],
    data_splits: List[Dict[str, str]],
):
    # create data card
    registry = db_registries.data
    a

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )
    registry.register_card(card=data_card)

    registry.load_card(uid=data_card.uid)