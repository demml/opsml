from scouter import DataProfile

from opsml.cards import DataCard
from opsml.data import NumpyData, PandasData, PolarsData
from opsml.profile.profile_data import DataProfiler
from opsml.registry import CardRegistries


def test_datacard_create_data_profile_pandas(
    db_registries: CardRegistries,
    iris_data: PandasData,
) -> None:
    # create data card
    registry = db_registries.data

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

    load_data_card: DataCard = registry.load_card(uid=data_card.uid)
    load_data_card.load_data_profile()

    assert load_data_card.data_profile is not None


def test_datacard_create_data_profile_polars(
    db_registries: CardRegistries,
    iris_data_polars: PolarsData,
) -> None:
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

    # should raise logging info if called again
    iris_data_polars.create_data_profile()

    registry.register_card(data_card)

    load_data_card: DataCard = registry.load_card(uid=data_card.uid)
    load_data_card.load_data_profile()

    assert data_card.data_profile is not None
    assert isinstance(data_card.data_profile, DataProfile)


def test_feed_data_profile(
    db_registries: CardRegistries,
    iris_data: PandasData,
) -> None:
    profile = DataProfiler().create_profile_report(data=iris_data.data)
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
    iris_data.create_data_profile()
    assert data_card.data_profile is not None


def test_datacard_numpy_profile_fail(numpy_data: NumpyData) -> None:

    numpy_data.create_data_profile()
