from opsml.data import PolarsData, DataSaveKwargs
from opsml.card import DataCard
import polars as pl
from pathlib import Path


def test_polars_datacard(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    interface = PolarsData(data=multi_type_polars_dataframe2)

    card = DataCard(interface=interface, name="test", repository="test")

    save_path = tmp_path / "test"
    save_path.mkdir()

    kwargs = {"compression": "gzip"}
    save_kwargs = DataSaveKwargs(data=kwargs)
    card.save(save_path, save_kwargs)

    data_save_path = (save_path / "data").with_suffix(".parquet")

    assert data_save_path.exists()

    card.load(save_path)
