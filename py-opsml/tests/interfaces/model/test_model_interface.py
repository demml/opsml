from opsml.model import ModelInterface, TaskType
from opsml.data import NumpyData, PandasData, PolarsData, ArrowData, TorchData
from opsml.types import DataType
from numpy.typing import NDArray
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa  # type: ignore
import torch
from typing import List, Dict


def test_model_interface_sample_data_numpy(numpy_array: NDArray[np.float64]):
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

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Numpy


def test_model_interface_sample_data_pandas(pandas_dataframe_num: pd.DataFrame):
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

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Pandas


def test_model_interface_sample_data_polars(polars_dataframe_num: pl.DataFrame):
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

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Polars


def test_model_interface_sample_data_arrow(arrow_num: pa.Table):
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

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Arrow


def test_model_interface_sample_data_torch(torch_tensor: torch.Tensor):
    """Test logic

    1. Create a ModelInterface object with sample_data as numpy_array
        - This sample data should be converted to TorchData Interface with sampled data

    2. Create new model interface with TorchData, should return same interface with sampled data
    """

    ##1
    assert torch_tensor.shape == (2, 3)
    model_interface = ModelInterface(sample_data=torch_tensor)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, TorchData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 3)

    ##2
    assert torch_tensor.shape == (2, 3)
    data_interface = TorchData(data=torch_tensor)
    model_interface = ModelInterface(sample_data=data_interface)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, TorchData)

    assert model_interface.sample_data.data is not None
    assert model_interface.sample_data.data.shape == (1, 3)
    assert id(model_interface.sample_data) == id(data_interface)

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.TorchTensor


def test_model_interface_sample_data_list(numpy_list: List[NDArray[np.float64]]):
    """Test logic

    1. Create a ModelInterface object with sample_data as a list of ndarays
        - This sample data should be iterated over and sliced
    """

    ##1
    assert len(numpy_list) == 2
    for data in numpy_list:
        assert data.shape == (2, 3)

    model_interface = ModelInterface(sample_data=numpy_list)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, list)

    ## assert each data is sliced
    for data in model_interface.sample_data:
        assert data.shape == (1, 3)

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.List


def test_model_interface_sample_data_tuple(numpy_tuple: tuple[NDArray[np.float64]]):
    """Test logic

    1. Create a ModelInterface object with sample_data as a tuple of ndarrays
        - This sample data should be iterated over and sliced
    """

    ##1
    assert len(numpy_tuple) == 2
    for data in numpy_tuple:
        assert data.shape == (2, 3)

    model_interface = ModelInterface(sample_data=numpy_tuple)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, tuple)

    ## assert each data is sliced
    for data in model_interface.sample_data:
        assert data.shape == (1, 3)

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Tuple


def test_model_interface_sample_data_dict(numpy_dict: Dict[str, NDArray[np.float64]]):
    """Test logic

    1. Create a ModelInterface object with sample_data as a Dictionary of ndarrays
        - This sample data should be iterated over and sliced
    """

    ##1
    assert len(numpy_dict.keys()) == 2
    for _, data in numpy_dict.items():
        assert data.shape == (2, 3)

    model_interface = ModelInterface(sample_data=numpy_dict)

    assert model_interface.sample_data is not None
    assert isinstance(model_interface.sample_data, dict)

    ## assert each data is sliced
    for _, data in model_interface.sample_data.items():
        assert data.shape == (1, 3)

    assert model_interface.task_type == TaskType.Undefined
    assert model_interface.data_type == DataType.Dict
