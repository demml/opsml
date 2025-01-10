from opsml.model import ModelInterface, TaskType
from opsml.data import NumpyData, DataType, PandasData, PolarsData, ArrowData
from numpy.typing import NDArray
from pathlib import Path
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa  # type: ignore


def test_model_interface_sample_data_numpy(
    tmp_path: Path, numpy_array: NDArray[np.float64]
):
    """Test logic

    1. Create a ModelInterface object with sample_data as numpy_array
        - This sample data should be converted to NumpyData Interface with sampled data

    2. Create new model interface with NumpyData, should return same interface with sampled data
    """

    ##1
    assert numpy_array.shape == (10, 100)
    model_interface = ModelInterface(sample_data=numpy_array)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, NumpyData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)

    ##2
    assert numpy_array.shape == (10, 100)
    data_interface = NumpyData(data=numpy_array)
    model_interface = ModelInterface(sample_data=data_interface)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, NumpyData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)
    assert id(model_interface.sample_data) == id(data_interface)

    assert model_interface.task_type == TaskType.Other
    assert model_interface.data_type == DataType.Numpy


def test_model_interface_sample_data_pandas(
    tmp_path: Path, pandas_dataframe_num: pd.DataFrame
):
    """Test logic

    1. Create a ModelInterface object with sample_data as numpy_array
        - This sample data should be converted to PandasData Interface with sampled data

    2. Create new model interface with PandasData, should return same interface with sampled data
    """

    ##1
    assert pandas_dataframe_num.shape == (10, 100)
    model_interface = ModelInterface(sample_data=pandas_dataframe_num)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, PandasData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)

    ##2
    assert pandas_dataframe_num.shape == (10, 100)
    data_interface = PandasData(data=pandas_dataframe_num)
    model_interface = ModelInterface(sample_data=data_interface)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, PandasData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)
    assert id(model_interface.sample_data) == id(data_interface)

    assert model_interface.task_type == TaskType.Other
    assert model_interface.data_type == DataType.Pandas


def test_model_interface_sample_data_polars(
    tmp_path: Path, polars_dataframe_num: pl.DataFrame
):
    """Test logic

    1. Create a ModelInterface object with sample_data as numpy_array
        - This sample data should be converted to PolarsData Interface with sampled data

    2. Create new model interface with PolarsData, should return same interface with sampled data
    """

    ##1
    assert polars_dataframe_num.shape == (10, 100)
    model_interface = ModelInterface(sample_data=polars_dataframe_num)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, PolarsData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)

    ##2
    assert polars_dataframe_num.shape == (10, 100)
    data_interface = PolarsData(data=polars_dataframe_num)
    model_interface = ModelInterface(sample_data=data_interface)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, PolarsData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)
    assert id(model_interface.sample_data) == id(data_interface)

    assert model_interface.task_type == TaskType.Other
    assert model_interface.data_type == DataType.Polars


def test_model_interface_sample_data_arrow(tmp_path: Path, arrow_num: pa.Table):
    """Test logic

    1. Create a ModelInterface object with sample_data as numpy_array
        - This sample data should be converted to ArrowData Interface with sampled data

    2. Create new model interface with ArrowData, should return same interface with sampled data
    """

    ##1
    assert arrow_num.shape == (10, 100)
    model_interface = ModelInterface(sample_data=arrow_num)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, ArrowData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)

    ##2
    assert arrow_num.shape == (10, 100)
    data_interface = ArrowData(data=arrow_num)
    model_interface = ModelInterface(sample_data=data_interface)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, ArrowData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 100)
    assert id(model_interface.sample_data) == id(data_interface)

    assert model_interface.task_type == TaskType.Other
    assert model_interface.data_type == DataType.Arrow
