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

The [`PandasData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_pandas.py) interface is used to store data from a `pandas` dataframe. Pandas data is converted and saved to [`parquet`](https://arrow.apache.org/docs/python/parquet.html) for fast writing and reading.


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

The [`PolarsData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_polars.py) interface is used to store data from a `polars` dataframe. Polars data is converted and saved to [`parquet`](https://arrow.apache.org/docs/python/parquet.html) for fast writing and reading.


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

The [`NumpyData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_numpy.py) interface is used to store numpy arrays. Numpy data is converted and saved as a [`Zarr`](https://zarr.readthedocs.io/en/stable/index.html) array for fast read and writes.


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

The [`ArrowData`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_arrow.py) interface is used to store numpy arrays. Numpy data is converted and saved as a [`parquet`](https://arrow.apache.org/docs/python/parquet.html) for fast writing and reading.

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
## Subclassing `DataInterface`

In the event that the currently supported `DataInterfaces` do not meet your needs, you can subclass the parent `DataInterface` and implement your own interface. However, there are a few requirements:

- `save_data` method must be overwritten to your desired logic and must accept a `path` argument
- `load_data` method must be overwritten to your desired logic and must accept a `path` argument
- `data_suffix` property must be overwritten to return your specific data suffix (e.g. `.csv`, `.json`, etc.)

These requirements are necessary for `Opsml` to properly save and load your data, as these are called during either saving or loading via the `DataCard`.

**Final Note** - It is up to you to make sure your subclass works as expected and is compatible with the `DataCard` class. If you feel your subclass is useful to others, please consider contributing it to the `Opsml` library. In addition, if using a custom subclass, others will not be able to load/use your `card` unless they have access to the custom subclass.

