from opsml import (
    DataInterface,
    DataType,
    OpsmlError,
    SqlLogic,
    DataSplit,
    DataSplits,
    IndiceSplit,
    DependentVars,
    NumpyData,
)
import numpy as np
from numpy.typing import NDArray
from pathlib import Path
import pytest


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

    data_interface.save_data(save_path)
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


def test_numpy_interface(numpy_array: NDArray[np.float64]):
    _ = NumpyData(data=numpy_array)

    with pytest.raises(OpsmlError) as error:
        _ = NumpyData(data=10)
