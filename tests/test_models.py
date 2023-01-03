import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml_data.helpers.exceptions import NotOfCorrectType
from opsml_data.registry.data_card import DataCard
from opsml_data.registry.models import DataSplit


def test_partition():
    split = {"label": "train", "column": "test", "column_value": 10}

    partition = DataSplit(**split)

    assert partition.column == "test"
    assert partition.column_value == 10

    split = {"label": "train", "start": 0, "stop": 10}

    partition = DataSplit(**split)

    assert partition.start == 0
    assert partition.stop == 10

    # this should fail
    new_data = {"label": "train", "col_fail": "test_fail", "val": 10}

    try:
        split = DataSplit(**new_data)
        raise NotOfCorrectType("Datasplit should fail for invalid keys")

    except ValueError as e:
        pass


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
        data_name="test_df",
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
            data_name="test_df",
            team="mlops",
            user_email="mlops.com",
            data_splits=splits,
        )

        splits = data_card.split_data()

        assert len(splits.dict().keys()) == 2
