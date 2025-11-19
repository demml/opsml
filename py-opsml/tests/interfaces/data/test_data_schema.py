from opsml.data import generate_feature_schema
from opsml.types import DataType
import polars as pl


def test_polars_interface(
    multi_type_polars_dataframe: pl.DataFrame,
):
    feature_map = generate_feature_schema(multi_type_polars_dataframe, DataType.Polars)

    assert feature_map["int8"].feature_type == "Int8"
    assert feature_map["int16"].feature_type == "Int16"
    assert feature_map["int32"].feature_type == "Int32"
    assert feature_map["int64"].feature_type == "Int64"
    assert feature_map["uint8"].feature_type == "UInt8"
    assert feature_map["uint16"].feature_type == "UInt16"
    assert feature_map["uint32"].feature_type == "UInt32"
    assert feature_map["float32"].feature_type == "Float32"
    assert feature_map["float64"].feature_type == "Float64"
    assert feature_map["decimal"].feature_type == "Decimal"
    assert feature_map["bool"].feature_type == "Boolean"
    assert feature_map["string"].feature_type == "String"
    assert feature_map["utf8"].feature_type == "String"
    assert feature_map["binary"].feature_type == "Binary"
    assert feature_map["date"].feature_type == "Date"
    assert feature_map["time"].feature_type == "Time"
    assert feature_map["datetime"].feature_type == "Datetime"
    assert feature_map["duration"].feature_type == "Duration"
    assert feature_map["categorical"].feature_type == "Categorical"
    assert feature_map["enum"].feature_type == "Enum"
    assert feature_map["object"].feature_type == "Object"
    assert feature_map["null"].feature_type == "Null"
    assert feature_map["list"].feature_type == "List"
    assert feature_map["array"].feature_type == "Array"
