import numpy as np
import pyarrow as pa
import pytest

from opsml.registry.data.splitter import DataSplit, DataSplitter, DataSplitterBase
from opsml.registry.data.types import AllowedDataType


def test_pyarrow_splitter(test_arrow_table: pa.Table):
    split = DataSplit(label="train", indices=np.array([0, 2]))
    label, data = DataSplitter.split(
        split=split, data=test_arrow_table, data_type=AllowedDataType.PYARROW, dependent_vars=[]
    )
    assert isinstance(data.X, pa.Table)


def test_base_splitter():
    split = DataSplit(label="train", indices=np.array([0, 2]))

    splitter = DataSplitterBase(split=split, dependent_vars=[])

    with pytest.raises(ValueError):
        splitter.column_name

    with pytest.raises(ValueError):
        splitter.column_value

    with pytest.raises(ValueError):
        splitter.start

    with pytest.raises(ValueError):
        splitter.stop

    split = DataSplit(label="train", start=0, stop=1)

    splitter = DataSplitterBase(split=split, dependent_vars=[])
    with pytest.raises(ValueError):
        splitter.indices
