from opsml.data import PolarsData, DataSaveKwargs, PandasData
from opsml.card import DataCard
import polars as pl
from pathlib import Path


def test_polars_datacard(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    interface = PolarsData(data=multi_type_polars_dataframe2)

    card = DataCard(interface=interface, name="test", space="test")

    assert card.interface is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    kwargs = {"compression": "gzip"}
    save_kwargs = DataSaveKwargs(data=kwargs)
    card.save(save_path, save_kwargs)

    data_save_path = (save_path / "data").with_suffix(".parquet")

    assert data_save_path.exists()

    card.load(save_path)


def test_pandas_datacard_data_profile(pandas_data: PandasData):
    card = DataCard(interface=pandas_data, name="test", space="test")

    assert card.interface is not None

    # validate creating a data profile by accessing interface via card getter attribute
    assert card.interface.data_profile is None
    card.create_data_profile()
    assert card.interface.data_profile is not None
