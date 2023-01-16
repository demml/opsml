import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml_artifacts.registry.cards.cards import DataCard


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_array"),
        lazy_fixture("test_df"),
    ],
)
def test_data_card_splits(test_data):

    splits = [
        {"label": "train", "start": 0, "stop": 2},
        {"label": "test", "start": 2, "stop": 4},
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=splits,
    )

    splits = data_card.split_data()

    assert len(splits.dict().keys()) == 2

    if isinstance(test_data, pd.DataFrame):
        splits = [
            {"label": "train", "column": "n_legs", "column_value": 2},
            {"label": "test", "column": "n_legs", "column_value": 4},
        ]

        data_card = DataCard(
            data=test_data,
            name="test_df",
            team="mlops",
            user_email="mlops.com",
            data_splits=splits,
        )

        splits = data_card.split_data()

        assert len(splits.dict().keys()) == 2
