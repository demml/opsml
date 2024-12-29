from opsml import DataInterface, DataType
import numpy as np
from numpy.typing import NDArray
from pathlib import Path


def test_data_interface(tmp_path: Path, numpy_array: NDArray[np.float64]):
    data_interface = DataInterface()
    assert data_interface is not None
    assert data_interface.data is None

    data_interface.data = numpy_array
    assert data_interface.data is not None

    assert data_interface.data_type == DataType.Base

    data_interface = DataInterface(data=numpy_array, sql_logic={"sql": "test_sql.sql"})

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

    data_interface.load_data(save_path)

    assert data_interface.data is not None
