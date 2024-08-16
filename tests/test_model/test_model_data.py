import pytest

from opsml.data import NumpyData, PandasData
from opsml.model.utils.data_helper import (
    FloatTypeConverter,
    ModelDataHelper,
    get_model_data,
)
from opsml.types import AllowedDataType

# most methods are tested as part of other unit tests


def test_model_data_base(numpy_data: NumpyData):
    model_data = ModelDataHelper(input_data=numpy_data.data, data_type=AllowedDataType.NUMPY.value)

    with pytest.raises(NotImplementedError):
        model_data.dtypes

    with pytest.raises(NotImplementedError):
        model_data.shape

    with pytest.raises(NotImplementedError):
        model_data.num_dtypes

    with pytest.raises(NotImplementedError):
        model_data.feature_dict


def test_dataframe(pandas_data: PandasData):
    """Test ModelData for pandas dataframe"""
    pd_data = get_model_data(input_data=pandas_data.data, data_type=AllowedDataType.PANDAS)

    assert isinstance(pd_data.shape, tuple)
    assert isinstance(pd_data.dtypes, list)
    assert isinstance(pd_data.feature_dict, dict)
    assert isinstance(pd_data.feature_types, zip)


def test_numpy(numpy_data: NumpyData):
    """Test ModelData for numpy array"""
    numpy_data = get_model_data(
        input_data=numpy_data.data,
        data_type=AllowedDataType.NUMPY,
    )

    assert isinstance(numpy_data.feature_dict, dict)

    with pytest.raises(ValueError):
        numpy_data.to_numpy()
    with pytest.raises(ValueError):
        numpy_data.dataframe_record()
    with pytest.raises(ValueError):
        numpy_data.convert_dataframe_column(column_type="test", convert_column_type="test")


def test_dictionary(numpy_data: NumpyData):
    """Test ModelData for dictionary"""
    data = {"test": numpy_data.data}
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
