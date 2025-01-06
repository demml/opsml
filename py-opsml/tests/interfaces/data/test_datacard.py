from opsml import PolarsData, DataCard, DataInterface
import polars as pl
from pathlib import Path


def test_polars_datacard(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    interface = PolarsData(data=multi_type_polars_dataframe2)

    card = DataCard(interface=interface, name="test", repository="test", contact="test")

    save_path = tmp_path / "test"
    save_path.mkdir()

    kwargs = {"compression": "gzip"}
    metadata = card.save(path=save_path, **kwargs)

    save_path = save_path / metadata.data_save_path

    assert save_path.exists()


def test_custom_datacard(
    multi_type_polars_dataframe2: pl.DataFrame,
    tmp_path: Path,
    custom_data_interface: type[DataInterface],
):
    interface = custom_data_interface(data=multi_type_polars_dataframe2)

    card = DataCard(interface=interface, name="test", repository="test", contact="test")

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = card.save(path=save_path)

    save_path = save_path / metadata.data_save_path

    assert save_path.exists()
    assert save_path.suffix == ".joblib"