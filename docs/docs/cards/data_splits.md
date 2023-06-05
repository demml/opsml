# Data Splits

In most data science workflows, it's common to split data into different subsets for analysis and comparison. In support of this, `DataCards` allow you to specify and split your data based on specific logic that is provided to a `DataSplit`.

### Split types

#### **Column Name and Value**

- Split data based on a column value. 
- Supports inequality signs. 
- Works with `Pandas` and `Polars` `DataFrames`.

**Example**

```python

import polars as pl
from opsml.registry import DataCard, DataSplit, CardInfo

info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

df = pl.DataFrame(
    {
        "foo": [1, 2, 3, 4, 5, 6],
        "bar": ["a", "b", "c", "d", "e", "f"],
        "y": [1, 2, 3, 4, 5, 6],
    }
)

datacard = DataCard(
    info=info,
    data=df
    data_splits = [
        DataSplit(label="train", column_name="fool", column_value=6, inequality="<"),
        DataSplit(label="test", column_name="foo", column_value=6)
    ]

)

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 5
    assert splits.test.X.shape[0] == 1
```

#### **Indices**

- Split data based on pre-defined indices
- Works with `NDArray`, `pyarrow.Table`, `pandas.DataFrame` and `polars.DataFrame`


```python

import numpy as np
from opsml.registry import DataCard, DataSplit, CardInfo

info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

data = np.random.rand(10, 10)

datacard = DataCard(
    info=info,
    data=data
    data_splits = [
        DataSplit(label="train", indices=[0,1,5])
    ]

)

splits = datacard.split_data()
assert splits.train.X.shape[0] == 3
```

#### **Start and Stop Slicing**

- Split data based on row slices with a start and stop index
- Works with `NDArray`, `pyarrow.Table`, `pandas.DataFrame` and `polars.DataFrame`


```python

import numpy as np
from opsml.registry import DataCard, DataSplit, CardInfo

info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

data = np.random.rand(10, 10)

datacard = DataCard(
    info=info,
    data=data
    data_splits = [
        DataSplit(label="train", start=0, stop=3)
    ]

)

splits = datacard.split_data()
assert splits.train.X.shape[0] == 3
```
