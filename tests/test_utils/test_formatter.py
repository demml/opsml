import numpy as np
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml.registry.data.formatter import DataFormatter


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_array"),
        lazy_fixture("test_df"),
        lazy_fixture("test_arrow_table"),
    ],
)
def test_convert_to_pyarrow(test_data):

    data = DataFormatter.convert_data_to_arrow(test_data)

    # test schema
    schema = DataFormatter.create_table_schema(data)
