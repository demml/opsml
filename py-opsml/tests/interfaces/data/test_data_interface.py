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
    DataSaveKwargs,
    ColumnSplit,
    ColType,
    Inequality,
)
from opsml.types import DataType

import numpy as np
import polars as pl
import pyarrow as pa  # type: ignore
from numpy.typing import NDArray
from pathlib import Path
import pytest
import torch
import pandas as pd


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

    metadata = data_interface.save(save_path)
    data_interface.data = None

    assert data_interface.data is None

    ## should raise an error if we try to save again
    with pytest.raises(RuntimeError) as error:
        data_interface.save(save_path)
    assert str(error.value) == "No data detected in interface for saving"

    data_interface.load(save_path, metadata.save_metadata)

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
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 5, 9],
        ),
    )

    interface = NumpyData(
        data=numpy_array,
        data_splits=DataSplits(
            [data_split],
        ),
    )

    assert interface.data is not None
    assert interface.data_type == DataType.Numpy
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(save_path)

    assert metadata.save_metadata.data_uri == Path("data.npy")
    assert metadata.data_type == DataType.Numpy

    with pytest.raises(RuntimeError):
        _ = NumpyData(data=10)

    interface.data = None
    assert interface.data is None

    interface.load(save_path, metadata.save_metadata)

    assert interface.data is not None

    interface.schema["numpy_array"].feature_type = "float64"
    interface.schema["numpy_array"].shape = [10, 100]

    data = interface.split_data()
    assert data["train"].x.shape == (3, 100)


def test_polars_interface(multi_type_polars_dataframe2: pl.DataFrame, tmp_path: Path):
    data_split = DataSplit(
        label="train",
        column_split=ColumnSplit(
            column_name="float64",
            column_value=1.0,
            column_type=ColType.Builtin,
        ),
    )
    interface = PolarsData(
        data=multi_type_polars_dataframe2,
        data_splits=[data_split],
    )

    split_data = interface.split_data()
    assert split_data["train"].x.shape == (1, 24)

    assert interface.data is not None
    assert interface.data_type == DataType.Polars
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    kwargs = {"compression": "gzip"}
    save_kwargs = DataSaveKwargs(data=kwargs)
    metadata = interface.save(save_path, save_kwargs)

    assert metadata.data_type == DataType.Polars
    assert interface.schema["int8"].feature_type == "Int8"
    assert interface.schema["int16"].feature_type == "Int16"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load(path=save_path, metadata=metadata.save_metadata)

    assert interface.data is not None

    with pytest.raises(RuntimeError):
        interface.data = 10


def test_pandas_interface(pandas_mixed_type_dataframe: pd.DataFrame, tmp_path: Path):
    data_split = DataSplit(
        label="train",
        column_split=ColumnSplit(
            column_name="year",
            column_value=2020,
            column_type=ColType.Builtin,
            inequality=Inequality.GreaterThanEqual,
        ),
    )

    interface = PandasData(
        data=pandas_mixed_type_dataframe,
        data_splits=[data_split],
    )

    assert interface.data is not None
    assert interface.data_type == DataType.Pandas
    assert interface.dependent_vars is not None
    assert interface.data_splits is not None
    assert interface.sql_logic is not None

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(path=save_path)

    assert metadata.data_type == DataType.Pandas
    assert interface.schema["n_legs"].feature_type == "int64"
    assert interface.schema["category"].feature_type == "category"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load(path=save_path, metadata=metadata.save_metadata)

    assert interface.data is not None

    for i in range(0, len(interface.data.columns)):
        assert (
            interface.data.dtypes.iloc[i] == pandas_mixed_type_dataframe.dtypes.iloc[i]
        )

    with pytest.raises(RuntimeError):
        interface.data = 10

    split_data = interface.split_data()
    assert split_data["train"].x.shape == (6, 5)


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
    assert interface.schema["n_legs"].feature_type == "int64"
    assert interface.schema["animals"].feature_type == "string"

    # set data to none
    interface.data = None

    assert interface.data is None

    interface.load(path=save_path, metadata=metadata.save_metadata)

    assert interface.data is not None

    with pytest.raises(RuntimeError):
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

    interface.load(path=save_path, metadata=metadata.save_metadata)

    assert interface.data is not None

    with pytest.raises(RuntimeError):
        interface.data = 10


def test_pandas_data_profile(pandas_dataframe_profile: pd.DataFrame):
    interface = PandasData(data=pandas_dataframe_profile)
    data_profile = interface.create_data_profile(compute_correlations=True)
    assert data_profile is not None
    # set data_profile to None
    interface.data_profile = None
    assert interface.data_profile is None

    # test setter
    interface.data_profile = data_profile
    assert interface.data_profile is not None
