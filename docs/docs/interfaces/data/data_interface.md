# Data Interface

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

`team`
: Team data belongs to

`contact`
: Contact information (can be anything you define such as an email or slack channel) (Required)


### Optional Arguments

`sql_logic`
: SQL query or path to sql file containing logic to build data. Required if `data` is not provided.

`data_splits`
: Split logic for your data. Optional list of `DataSplit`. See [DataSplit](./data_splits.md) for more information.

`data_profile`
: `ydata-profiling` data profile. This can also be generated via `create_data_profile` method after instantiation.

## Subclassing `DataInterface`

In the event that the currently supported `DataInterfaces` do not meet your needs, you can subclass the parent `DataInterface` and implement your own interface. However, there are a few requirements:

- `save_data` method must be overwritten to your desired logic and must accept a `path` argument
- `load_data` method must be overwritten to your desired logic and must accept a `path` argument
- `data_suffix` property must be overwritten to return your specific data suffix (e.g. `.csv`, `.json`, etc.)

These requirements are necessary for `Opsml` to properly save and load your data, as these are called during either saving or loading via the `DataCard`.

**Final Note** - It is up to you to make sure your subclass works as expected and is compatible with the `DataCard` class. If you feel your subclass is useful to others, please consider contributing it to the `Opsml` library.