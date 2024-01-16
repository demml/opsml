import pytest

from opsml.data import SqlData


def test_sql_interface():
    interface = SqlData(
        sql_logic={"query": "SELECT * FROM table"},
        feature_descriptions={"a": "b"},
    )

    added_sql_name = "add_sql"
    added_sql_query = "select * from test_table"
    interface.add_sql(name=added_sql_name, query=added_sql_query)

    assert interface.data_type == "sql"
    assert interface.name() == "SqlData"
    assert interface.sql_logic.get("query") == "SELECT * FROM table"
    assert interface.sql_logic.get(added_sql_name) == added_sql_query
    assert interface.feature_descriptions == {"a": "b"}

    ### Test add failure
    with pytest.raises(FileNotFoundError):
        interface.add_sql(name="fail", filename="fail.sql")

    with pytest.raises(ValueError):
        interface.add_sql(name="fail")

    with pytest.raises(ValueError):
        SqlData(
            sql_logic={"query": "fail.sql"},
            feature_descriptions={"a": "b"},
        )


def test_backup_interfaces():
    from opsml.data.interfaces.backups import ImageDatasetNoModule, TorchDataNoModule
    from opsml.model.interfaces.backups import (
        HuggingFaceModelNoModule,
        LightGBMModelNoModule,
        LightningModelNoModule,
        SklearnModelNoModule,
        TensorFlowModelNoModule,
        TorchModelNoModule,
        XGBoostModelNoModule,
    )

    for model in [
        TensorFlowModelNoModule,
        LightGBMModelNoModule,
        LightningModelNoModule,
        SklearnModelNoModule,
        TorchModelNoModule,
        HuggingFaceModelNoModule,
        XGBoostModelNoModule,
        TorchDataNoModule,
        ImageDatasetNoModule,
    ]:
        assert model.name() == model.__name__
        with pytest.raises(ModuleNotFoundError):
            model()
