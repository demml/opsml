from opsml_data.connector.data_formatter import DataFormatter
import numpy as np


def test_convert_to_pyarrow(test_array, test_df, test_arrow_table):

    for i in [test_array, test_df, test_arrow_table]:
        data = DataFormatter.convert_data_to_arrow(i)


def test_schema(test_arrow_table):

    schema = DataFormatter.get_schema(test_arrow_table)
