from typing import Dict
import pandas as pd
from ydata_profiling import ProfileReport
import numpy as np
from opsml.registry.sql.registry import CardRegistry
from opsml.registry import DataCard
from opsml.profile.profile_data import DataProfiler
from sklearn.model_selection import train_test_split


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

    data_card = registry.load_card(uid=data_card.uid)

    assert data_card.data_profile is not None


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

    # test profiling with sample
    data_card = DataCard(
        data=iris_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    data_card.create_data_profile(sample_perc=0.50)
    assert data_card.data_profile is not None


def test_compare_data_profile(
    db_registries: Dict[str, CardRegistry],
    iris_data: pd.DataFrame,
):
    # create data card
    registry = db_registries["data"]

    # Split indices
    indices = np.arange(iris_data.shape[0])

    # usual train-val split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

    data_card = DataCard(
        data=iris_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=[
            {"label": "train", "indices": train_idx},
            {"label": "test", "indices": test_idx},
        ],
    )

    splits = data_card.split_data()

    train_profile = DataProfiler.create_profile_report(splits.train.X, name="train")
    test_profile = DataProfiler.create_profile_report(splits.test.X, name="test")

    comparison = DataProfiler.compare_reports([train_profile, test_profile])

    assert isinstance(comparison, ProfileReport)
