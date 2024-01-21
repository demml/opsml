# Data Interface

The `DataInterface` is the primary interface for working with data in `Opsml`. It is designed to be subclassed and can be used to store data in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `PandasData`: Stores data from a pandas dataframe
- `NumpyData`: Stores data from a numpy array
- `PolarsData`: Stores data from a polars dataframe
- `ArrowData`: Stores data from a pyarrow table
- `ImageDataset`: Stores data from a directory of images
- `TextDataset`: Stores data from a directory of text files
- `TorchtData`: Stores data from a torch tensor(s)
- `SqlData`: Stores sql text

### Required Arguments

`data`: See data interface for required type
: Data to save. See subclasses for supported data types

`name`: `str`
: Name for the data

`repository`: `str`
: Repository data belongs to

`contact`: `str`
: Contact information (can be anything you define such as an email or slack channel) (Required)


### Optional Arguments

`sql_logic`: `Dict[str, str]`
: SQL query or path to sql file containing logic to build data. Required if `data` is not provided.

`data_splits`: `List[DataSplit]`
: Split logic for your data. Optional list of `DataSplit`. See [DataSplit](./data_splits.md) for more information.

`data_profile`: `Optional[ProfileReport]`
: `ydata-profiling` data profile. This can also be generated via `create_data_profile` method after instantiation. See [DataProfile](./data_profile.md) for more information.

`feature_map`: `Dict[str, Feature]`
: Feature map for your data. Optional dictionary of `Feature`. See [Feature](./feature.md) for more information. This is automatically inferred from data.

`feature_descriptions`: `Dict[str, str]`
: Optional dictionary of feature descriptions.


---
## PandasData

Information about the `PandasData` interface.

|  |  |
| --- | --- |
| **Data Type** | `pandas.DataFrame` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html)  |
| **Source** | [`PandasData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_pandas.py) |

### Example

```py hl_lines="1  11"
from opsml import PandasData, CardInfo, DataCard, CardRegistry
from opsml.helpers.data import create_fake_data

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

# create fake data
X, _ = create_fake_data(n_samples=1000, task_type="regression")

# Create data interface
interface = PandasData(data=X)

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## PolarsData

Information about the `PandasData` interface.

|  |  |
| --- | --- |
| **Data Type** | `polars.DataFrame` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html)  |
| **Source** | [`PolarsData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_polars.py) |



### Example

```python hl_lines="1  11"
from opsml import PolarsData, CardInfo, DataCard, CardRegistry
from opsml.helpers.data import create_fake_data

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

# create fake data
X, _ = create_fake_data(n_samples=1000, task_type="regression", to_polars=True)

# Create data interface
interface = PolarsData(data=X)

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## NumpyData

Information about the `NumpyData` interface.

|  |  |
| --- | --- |
| **Data Type** | `np.ndarray` |
| **Save Format** | [`Zarr`](https://zarr.readthedocs.io/en/stable/index.html)  |
| **Source** | [`NumpyData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_numpy.py) |


### Example

```python hl_lines="1  8"
from opsml import NumpyData, CardInfo, DataCard, CardRegistry
import numpy as np

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

data = np.random.rand(10, 100)
interface = NumpyData(data=data)

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## ArrowData

Information about the `ArrowData` interface.

|  |  |
| --- | --- |
| **Data Type** | `pa.Table` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html)  |
| **Source** | [`ArrowData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_arrow.py) |

### Example

```python hl_lines="1  12"
from opsml import ArrowData, CardInfo, DataCard, CardRegistry
import pyarrow as pa

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

n_legs = pa.array([2, 4, 5, 100])
animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
names = ["n_legs", "animals"]
table = pa.Table.from_arrays([n_legs, animals], names=names)

interface = ArrowData(data=table)

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## TorchData

Information about the `TorchData` interface.

|  |  |
| --- | --- |
| **Data Type** | `torch.Tensor` |
| **Save Format** | [`torch`](https://pytorch.org/tutorials/beginner/saving_loading_models.html)  |
| **Source** | [`TorchData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_torch.py) |

### Example

```python hl_lines="1  9"
from opsml import TorchData, CardInfo, DataCard, CardRegistry
import torch

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

X = torch.Tensor([[1.0], [51.0], [89.0]])

interface = TorchData(data=table)

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## SqlData

SqlData is an interface for storing sql logic in the event that you prefer to not save the data itself. This is useful for large datasets that you may not want to store in `Opsml` but still want to keep track of the logic used to generate the data.

|  |  |
| --- | --- |
| **Data Type** | `Dict[str, str]` |
| **Save Format** | `sql file` |
| **Source** | [`SqlData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_sql.py) |

### Example

```python hl_lines="1  6 10"
from opsml import SqlData, CardInfo, DataCard, CardRegistry

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

data = SqlData(sql_logic={"my_logic": "select * from test_table"})

# or this would work

data = SqlData(sql_logic={"my_logic": "path/to/file.sql"})

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```

---
## Subclassing `DataInterface`

In the event that the currently supported `DataInterfaces` do not meet your needs, you can subclass the parent `DataInterface` and implement your own interface. However, there are a few requirements:

- `save_data` method must be overwritten to your desired logic and must accept a `path` argument
- `load_data` method must be overwritten to your desired logic and must accept a `path` argument
- `data_suffix` property must be overwritten to return your specific data suffix (e.g. `.csv`, `.json`, etc.)

These requirements are necessary for `Opsml` to properly save and load your data, as these are called during either saving or loading via the `DataCard`.


### Example

```python
from opsml import DataInterface, CardInfo, DataCard, CardRegistry

info = CardInfo(name="data", repository="opsml", contact="opsml_user")
registry = CardRegistry("data")

# DataInterface is a pydantic BaseModel
class MyDataInterface(DataInterface):
    
    data: DataType

    def save_data(self, path):
        # save logic here

    def load_data(self, path):
        # load logic here

    @property
    def data_suffix(self):
        return ".my_data"

interface = MyDataInterface(data={{my_data}})

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
registry.register_card(card=datacard)

# Now you can load your data via the registry
# you will need to supply the interface subclass
datacard = registry.load_card(uid=datacard.uid, interface=MyDataInterface)
```

### **Final Note** 
It is up to you to make sure your subclass works as expected and is compatible with the `DataCard` class. If you feel your subclass is useful to others, please consider contributing it to the `Opsml` library. In addition, if using a custom subclass, others will not be able to load/use your `card` unless they have access to the custom subclass.
