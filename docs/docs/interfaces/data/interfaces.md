# Interfaces

As mentioned in the [overview](../overview.md), the `DataInterface` supports the following subclasses:

## Data Interface

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

`data`
: Data to save. See subclasses for supported data types

`name`
: Name for the data

`repository`
: Repository data belongs to

`contact`
: Contact information (can be anything you define such as an email or slack channel) (Required)


### Optional Arguments

`sql_logic`
: SQL query or path to sql file containing logic to build data. Required if `data` is not provided.

`data_splits`
: Split logic for your data. Optional list of `DataSplit`. See [DataSplit](./data_splits.md) for more information.

`data_profile`
: `ydata-profiling` data profile. This can also be generated via `create_data_profile` method after instantiation.


---
## PandasData

Information about the `PandasData` interface.

|  |  |
| --- | --- |
| **Data Type** | `pandas.DataFrame` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html)  |
| **Source** | [`PandasData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_pandas.py) |

### Example

```py hl_lines="1  10"
from opsml import PandasData, CardInfo, DataCard, CardRegistry

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

```python hl_lines="1  10"
from opsml import PolarsData, CardInfo, DataCard, CardRegistry

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

```python hl_lines="1  7"
from opsml import NumpyData, CardInfo, DataCard, CardRegistry

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

```python hl_lines="1  8"
from opsml import TorchData, CardInfo, DataCard, CardRegistry

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
## Dataset

In addition to `DataInterface` classes, `opsml` also provides a `Dataset` class that is used for when working with text or image data.

### Required Arguments

`data_dir`
: Path to directory containing data

`shard_size`
: Size of each shard. Defaults to `512MB`

### Optional Arguments

`splits`
: Dictionary of splits. Defaults to `{}` This is automatically inferred from directory structure

`description`
: Description of dataset. Defaults to `Description()`

### Dataset Saving and Loading

Datasets are saved via `pyarrow` reader and writers. This allows for efficient loading and saving of datasets. For saving, `Dataset` splits are saved as parquet files based on the specified `shard` size. During loading, the dataset is loaded based on both `batch_size` and `chunk_size` arguments. The `batch_size` argument is used to specify the number of rows to load at a time. The `chunk_size` argument is used to split the batch by `n` chunks. Both of these arguments are used to control memory usage during loading.


### ImageDataset

|  |  |
| --- | --- |
| **Data Type** | `Directory of images` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html) |
| **Source** | [`ImageDataset`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_image.py) |


---
## Subclassing `DataInterface`

In the event that the currently supported `DataInterfaces` do not meet your needs, you can subclass the parent `DataInterface` and implement your own interface. However, there are a few requirements:

- `save_data` method must be overwritten to your desired logic and must accept a `path` argument
- `load_data` method must be overwritten to your desired logic and must accept a `path` argument
- `data_suffix` property must be overwritten to return your specific data suffix (e.g. `.csv`, `.json`, etc.)

These requirements are necessary for `Opsml` to properly save and load your data, as these are called during either saving or loading via the `DataCard`.

**Final Note** - It is up to you to make sure your subclass works as expected and is compatible with the `DataCard` class. If you feel your subclass is useful to others, please consider contributing it to the `Opsml` library. In addition, if using a custom subclass, others will not be able to load/use your `card` unless they have access to the custom subclass.

