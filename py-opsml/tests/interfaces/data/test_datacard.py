from opsml import PolarsData, DataType, DataCard
import polars as pl
from pathlib import Path


def test_polars_interface(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    interface = PolarsData(data=multi_type_polars_dataframe2)

    assert interface.data is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    kwargs = {"compression": "gzip"}
    metadata = interface.save(path=save_path, **kwargs)

    assert metadata.data_type == DataType.Polars
    assert interface.feature_map["int8"].feature_type == "Int8"
    assert interface.feature_map["int16"].feature_type == "Int16"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load_data(path=save_path)

    assert interface.data is not None

    DataCard(interface=interface, name="test", repository="test", contact="test")
