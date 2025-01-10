from opsml.model import ModelInterface, TaskType
from opsml.data import NumpyData, DataType
from numpy.typing import NDArray
from pathlib import Path
import numpy as np


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
