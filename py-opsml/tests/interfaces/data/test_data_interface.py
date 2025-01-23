from opsml.data import (
    DataInterface,
    NumpyData,
    PolarsData,
    PandasData,
    ArrowData,
    TorchData,
    SqlLogic,
    DataSplits,
    DataSplit,
    IndiceSplit,
    DependentVars,
    DataType,
)
from opsml.core import OpsmlError
import numpy as np
import polars as pl
import pyarrow as pa  # type: ignore
from numpy.typing import NDArray
from pathlib import Path
import pytest
import torch
import pandas as pd
from typing import Tuple, Any


def test_data_interface(tmp_path: Path, numpy_array: NDArray[np.float64]):
    data_interface = DataInterface()
    assert data_interface is not None
    assert data_interface.data is None

    data_interface.data = numpy_array
    assert data_interface.data is not None

    assert data_interface.data_type == DataType.Base

    sql_logic = SqlLogic(queries={"sql": "test_sql.sql"})

    data_interface = DataInterface(data=numpy_array, sql_logic=sql_logic)

    assert (
        data_interface.sql_logic["sql"] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"
    )

    data_interface.add_sql_logic(name="sql2", filepath="test_sql.sql")

    assert (
        data_interface.sql_logic["sql2"] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"
    )

    save_path = tmp_path / "test"
    save_path.mkdir()

    data_interface.save(save_path)
    data_interface.data = None

    assert data_interface.data is None

    ## should raise an error if we try to save again
    with pytest.raises(OpsmlError) as error:
        data_interface.save_data(save_path)
    assert str(error.value) == "No data detected in interface for saving"

    data_interface.load_data(save_path)

    assert data_interface.data is not None


def test_data_split(numpy_array: NDArray[np.float64]):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 5, 9],
        ),
    )

    interface = DataInterface(data=numpy_array, data_splits=[data_split])
    interface = DataInterface(data=numpy_array, data_splits=DataSplits([data_split]))

    # update the data split
    data_split.label = "test"

    assert data_split.label == "test"

    interface.data_splits = DataSplits([data_split])

    assert interface.data_splits.splits[0].label == "test"

    interface.dependent_vars = DependentVars(["test"])

    assert interface.dependent_vars.column_names[0] == "test"


def test_numpy_interface(tmp_path: Path, numpy_array: NDArray[np.float64]):
    interface = NumpyData(data=numpy_array)

    assert interface.data is not None
    assert interface.data_type == DataType.Numpy
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(save_path)

    assert metadata.data_save_path == "data.npy"
    assert metadata.data_type == DataType.Numpy

    with pytest.raises(OpsmlError):
        _ = NumpyData(data=10)

    interface.data = None
    assert interface.data is None

    interface.load_data(save_path)

    assert interface.data is not None

    interface.feature_map["numpy_array"].feature_type = "float64"
    interface.feature_map["numpy_array"].shape = [10, 100]


def test_polars_interface(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    interface = PolarsData(data=multi_type_polars_dataframe2)

    assert interface.data is not None
    assert interface.data_type == DataType.Polars
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

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

    with pytest.raises(OpsmlError):
        interface.data = 10


def test_pandas_interface(pandas_mixed_type_dataframe: pd.DataFrame, tmp_path: Path):
    interface = PandasData(data=pandas_mixed_type_dataframe)

    assert interface.data is not None
    assert interface.data_type == DataType.Pandas
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(path=save_path)

    assert metadata.data_type == DataType.Pandas
    assert interface.feature_map["n_legs"].feature_type == "int64"
    assert interface.feature_map["category"].feature_type == "category"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load_data(path=save_path)

    assert interface.data is not None

    for i in range(0, len(interface.data.columns)):
        assert (
            interface.data.dtypes.iloc[i] == pandas_mixed_type_dataframe.dtypes.iloc[i]
        )

    with pytest.raises(OpsmlError):
        interface.data = 10


def test_arrow_interface(arrow_dataframe: pa.Table, tmp_path: Path):
    interface = ArrowData(data=arrow_dataframe)

    assert interface.data is not None
    assert interface.data_type == DataType.Arrow
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(path=save_path)

    assert metadata.data_type == DataType.Arrow
    assert interface.feature_map["n_legs"].feature_type == "int64"
    assert interface.feature_map["animals"].feature_type == "string"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load_data(path=save_path)

    assert interface.data is not None

    with pytest.raises(OpsmlError):
        interface.data = 10


def test_torch_data(torch_tensor: torch.Tensor, tmp_path: Path):
    interface = TorchData(data=torch_tensor)

    assert interface.data is not None
    assert interface.data_type == DataType.TorchTensor
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(path=save_path)

    assert metadata.data_type == DataType.TorchTensor

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load_data(path=save_path)

    assert interface.data is not None

    with pytest.raises(OpsmlError):
        interface.data = 10


def test_pandas_data_profile(pandas_dataframe_profile: pd.DataFrame):
    interface = PandasData(data=pandas_dataframe_profile)
    data_profile = interface.create_data_profile(compute_correlations=True)
    assert data_profile is not None


def test_torch_dataset(
    tmp_path: Path, torch_dataset: Tuple[torch.utils.data.Dataset, Any]
):
    dataset, custom_class = torch_dataset
    interface = TorchData(data=dataset)

    assert interface.data is not None
    assert interface.data_type == DataType.TorchDataset
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(path=save_path, **{"torch_dataset": custom_class})

    # assert metadata.data_type == DataType.TorchDataset


#
## set data to none
# interface.data = None
#
# assert interface.data is None
#
# interface.load_data(path=save_path,
#
# assert interface.data is not None
