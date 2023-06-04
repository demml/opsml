from opsml.registry.data.splitter import DataSplitter, DataSplit
import numpy as np
import pyarrow as pa


def test_pyarrow_splitter(test_arrow_table):
    split = DataSplit(label="train", indices=np.array([0, 2]))
    label, data = DataSplitter.split(split=split, data=test_arrow_table)
    assert isinstance(data.X, pa.Table)
