from opsml.model.data_helper import FloatTypeConverter, get_model_data, ModelDataHelper
from opsml.registry.data.types import AllowedDataType
import pytest
from numpy.typing import NDArray
import pandas as pd

# most methods are tested as part of other unit tests


def test_model_data_base(test_array: NDArray):
    model_data = ModelDataHelper(input_data=test_array)

    with pytest.raises(NotImplementedError):
        model_data.dtypes

    with pytest.raises(NotImplementedError):
        model_data.shape

    with pytest.raises(NotImplementedError):
        model_data.num_dtypes

    with pytest.raises(NotImplementedError):
        model_data.feature_dict


def test_dataframe(test_df: pd.DataFrame):
    """Test ModelData for pandas dataframe"""
    pd_data = get_model_data(input_data=test_df, data_type=AllowedDataType.PANDAS)

    assert isinstance(pd_data.shape, tuple)
    assert isinstance(pd_data.dtypes, list)
    assert isinstance(pd_data.feature_dict, dict)
    assert isinstance(pd_data.feature_types, zip)


def test_numpy(test_array: NDArray):
    """Test ModelData for numpy array"""
    numpy_data = get_model_data(
        input_data=test_array,
        data_type=AllowedDataType.NUMPY,
    )

    assert isinstance(numpy_data.feature_dict, dict)

    with pytest.raises(ValueError):
        numpy_data.to_numpy()
    with pytest.raises(ValueError):
        numpy_data.dataframe_record()
    with pytest.raises(ValueError):
        numpy_data.convert_dataframe_column(column_type="test", convert_column_type="test")


def test_dictionary(test_array: NDArray):
    """Test ModelData for dictionary"""
    data = {"test": test_array}
    dict_data = get_model_data(
        input_data=data,
        data_type=AllowedDataType.DICT,
    )

    assert isinstance(dict_data.feature_dict, dict)
    assert isinstance(dict_data.num_dtypes, int)
    assert isinstance(dict_data.features, list)

    with pytest.raises(ValueError):
        dict_data.to_numpy()
    with pytest.raises(ValueError):
        dict_data.dataframe_record()

    converter = FloatTypeConverter(convert_all=True)

    converter.convert_to_float(data=data)

    converter = FloatTypeConverter(convert_all=False)

    converter.convert_to_float(data=data)
