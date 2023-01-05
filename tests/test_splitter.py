from opsml_data.registry.splitter import DataSplitter
import pandas as pd
import numpy as np


def test_pandas_splitter(test_df):
    split = {"label": "train", "start": 0, "stop": 2}
    label, data = DataSplitter(split_attributes=split).split(data=test_df)
    assert isinstance(data, pd.DataFrame)

    split = {"label": "train", "column": "year", "column_value": 2020}
    label, data = DataSplitter(split_attributes=split).split(data=test_df)
    assert isinstance(data, pd.DataFrame)

    split = {"label": "train", "indices": [0, 1, 2]}
    label, data = DataSplitter(split_attributes=split).split(data=test_df)
    assert isinstance(data, pd.DataFrame)


def test_numpy_splitter(test_array):
    split = {"label": "train", "start": 0, "stop": 2}
    label, data = DataSplitter(split_attributes=split).split(data=test_array)
    assert isinstance(data, np.ndarray)

    split = {"label": "train", "indices": [0, 2, 3]}
    label, data = DataSplitter(split_attributes=split).split(data=test_array)
    assert isinstance(data, np.ndarray)
