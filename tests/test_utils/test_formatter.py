import numpy as np
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.data.types import AllowedDataType
from opsml.registry.data.formatter import DataFormatter
import pandas as pd
import polars as pl
import pyarrow as pa


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_array"),
        lazy_fixture("test_df"),
        lazy_fixture("test_arrow_table"),
        lazy_fixture("test_polars_dataframe"),
    ],
)
def test_convert_to_pyarrow(test_data):
    if isinstance(test_data, np.ndarray):
        data_type = AllowedDataType.NUMPY
    elif isinstance(test_data, pd.DataFrame):
        data_type = AllowedDataType.PANDAS
    elif isinstance(test_data, pl.DataFrame):
        data_type = AllowedDataType.POLARS
    elif isinstance(test_data, pa.Table):
        data_type = AllowedDataType.PYARROW

    data = DataFormatter.convert_data_to_arrow(test_data, data_type)

    # test schema
    DataFormatter.create_table_schema(data)
