# Data Splits

In most data science workflows, it's common to split data into different subsets for analysis and comparison. In support of this, `DataInterface` subclasses allow you to specify and split your data based on specific logic that is provided to a `DataSplit`.

### Split types

#### **Column Name and Value**

- Split data based on a column value. 
- Supports inequality signs. 
- Works with `Pandas` and `Polars` `DataFrames`.

**Example**

```python hl_lines="2  18-19"
import polars as pl
from opsml import PolarsData, DataSplit, CardInfo

info = CardInfo(name="data", repository="mlops", contact="user@mlops.com")

df = pl.DataFrame(
    {
        "foo": [1, 2, 3, 4, 5, 6],
        "bar": ["a", "b", "c", "d", "e", "f"],
        "y": [1, 2, 3, 4, 5, 6],
    }
)

interface = PolarsData(
    info=info,
    data=df,
    data_splits = [
        DataSplit(label="train", column_name="foo", column_value=6, inequality="<"),
        DataSplit(label="test", column_name="foo", column_value=6)
    ]

)

splits = interface.split_data()
assert splits.train.X.shape[0] == 5
assert splits.test.X.shape[0] == 1
```

#### **Indices**

- Split data based on pre-defined indices
- Works with `NDArray`, `pyarrow.Table`, `pandas.DataFrame` and `polars.DataFrame`


```python hl_lines="2  12"
import numpy as np
from opsml import NumpyData, DataSplit, CardInfo

info = CardInfo(name="data", repository="mlops", contact="user@mlops.com")

data = np.random.rand(10, 10)

interface = NumpyData(
    info=info,
    data=data,
    data_splits = [
        DataSplit(label="train", indices=[0,1,5])
    ]

)

splits = interface.split_data()
assert splits.train.X.shape[0] == 3
```

#### **Start and Stop Slicing**

- Split data based on row slices with a start and stop index
- Works with `NDArray`, `pyarrow.Table`, `pandas.DataFrame` and `polars.DataFrame`


```python hl_lines="2  12"
import numpy as np
from opsml import NumpyData, DataSplit, CardInfo

info = CardInfo(name="data", repository="mlops", contact="user@mlops.com")

data = np.random.rand(10, 10)

interface = NumpyData(
    info=info,
    data=data,
    data_splits = [
        DataSplit(label="train", start=0, stop=3)
    ]

)

splits = interface.split_data()
assert splits.train.X.shape[0] == 3
```

::: opsml.DataSplit
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3