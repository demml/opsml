import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split
from ydata_profiling import ProfileReport

from opsml.cards import DataCard, DataSplit
from opsml.data import NumpyData, PandasData, PolarsData
from opsml.profile.profile_data import DataProfiler
from opsml.registry import CardRegistries


def test_datacard_create_data_profile_pandas(
    db_registries: CardRegistries,
    iris_data: PandasData,
):
    # create data card
    registry = db_registries.data

    iris_data.data["date_"] = pd.Timestamp.today().strftime("%Y-%m-%d")
    iris_data.create_data_profile()

    # should raise logging info if called again
    iris_data.create_data_profile()

    data_card = DataCard(
        interface=iris_data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    registry.register_card(data_card)

    data_card: DataCard = registry.load_card(uid=data_card.uid)
    data_card.load_data_profile()

    assert data_card.data_profile is not None


def test_datacard_create_data_profile_polars(
    db_registries: CardRegistries,
    iris_data_polars: PolarsData,
):
    # create data card
    registry = db_registries.data
    data_card = DataCard(
        interface=iris_data_polars,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    # test non-sample path
    iris_data_polars.create_data_profile()

    # test sampling path
    iris_data_polars.create_data_profile(sample_perc=0.5)

    # should raise logging info if called again
    iris_data_polars.create_data_profile()

    registry.register_card(data_card)

    data_card: DataCard = registry.load_card(uid=data_card.uid)
    data_card.load_data_profile()

    assert data_card.data_profile is not None
    assert isinstance(data_card.data_profile, ProfileReport)


def test_feed_data_profile(
    db_registries: CardRegistries,
    iris_data: PandasData,
):
    profile = ProfileReport(iris_data.data, title="Profiling Report")
    iris_data.data_profile = profile

    data_card = DataCard(
        interface=iris_data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    # test profiling with sample
    data_card = DataCard(
        interface=iris_data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    iris_data.data_profile = None
    iris_data.create_data_profile(sample_perc=0.50)
    assert data_card.data_profile is not None


def test_compare_data_profile(
    db_registries: CardRegistries,
    iris_data: PandasData,
):
    # Split indices
    indices = np.arange(iris_data.data.shape[0])
    # usual train-val split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

    iris_data.data_splits = [
        DataSplit(label="train", indices=train_idx),
        DataSplit(label="test", indices=test_idx),
    ]

    data_card = DataCard(
        interface=iris_data,
        name="test_df",
        repository="mlops",
        contact="mlops.com",
    )

    splits = data_card.split_data()

    train_profile = DataProfiler.create_profile_report(splits.train.X, name="train")
    test_profile = DataProfiler.create_profile_report(splits.test.X, name="test")

    comparison = DataProfiler.compare_reports([train_profile, test_profile])

    assert isinstance(comparison, ProfileReport)


def test_datacard_numpy_profile_fail(numpy_data: NumpyData):

    with pytest.raises(ValueError):
        numpy_data.create_data_profile()
