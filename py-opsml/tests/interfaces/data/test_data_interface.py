from opsml import DataInterface, DataType
import numpy as np
from numpy.typing import NDArray


def test_data_interface(numpy_array: NDArray[np.float64]):
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
