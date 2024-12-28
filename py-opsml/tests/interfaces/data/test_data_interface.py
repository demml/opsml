from opsml import DataInterface, DataType


def test_data_interface():
    data_interface = DataInterface()
    assert data_interface is not None

    assert data_interface.data_type == DataType.Base

    data_interface = DataInterface(sql_logic={"sql": "test_sql.sql"})

    assert (
        data_interface.sql_logic["sql"] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"
    )

    data_interface.add_sql_logic(name="sql2", filepath="test_sql.sql")

    assert (
        data_interface.sql_logic["sql2"] == "SELECT ORDER_ID FROM TEST_TABLE limit 100"
    )
