# DataCard

DataCards are cards for storing, splitting, versioning, and tracking data. DataCards currently support `pd.DataFrames`, `np.Arrays`, and `pyarrow.Tables`.

## Features
- **shareable**: All cards including DataCards are shareable and searchable.
- **auto-schema**: Automatic shema detection and feature map creation for features and feature data types.
- **data-conversion**: Auto-conversion to either parquet (pa.Table, pd.DataFrame) or zarr (np.Arrays) for fast reading and writing to storage.
- **data_splits**: Define split logic for your data to generate splits (i.e., train, test, eval)
- **extra-info**: Additional optional arguments that allow you to associate your data with feature descriptions or extra info (sql scripts etc.)
- **versioning**: SemVer for your data.

## Creating a Card

```py
# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse


# Split indices
indices = np.arange(data.shape[0])

# usual train-val split
train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card = DataCard(
    info=card_info,
    data=data,
    dependent_vars=["Pulse"],
    # define splits
    data_splits=[
        DataSplit(label="train", indcies=train_idx),
        DataSplit(label="test", indcies=test_idx),
    ],
)

# splits look good
splits = data_card.split_data()
print(splits.train.X.head())

"""   
    Chins  Situps  Jumps
0    5.0   162.0   60.0
1    2.0   110.0   60.0
2   12.0   101.0  101.0
3   12.0   105.0   37.0
4   13.0   155.0   58.0
"""

data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)
print(data_card.version)
# > 1.0.0

# list cards
cards = data_registry.list_cards(
    uid=data_card.uid, 
    as_dataframe=False,
    )  # can also supply, name, team, version
print(cards[0])

```
*(Code will run as-is)*

Output:

```json
{
    "name": "linnerrud",
    "date": "2023-04-28",
    "version": "1.0.0",
    "data_uri": "opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.0.0/linnerrud.parquet",
    "runcard_uid": None,
    "datacard_uri": "opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.0.0/datacard.joblib",
    "uid": "06a28a3bc2504bdd83c20a622439236d",
    "app_env": "staging",
    "timestamp": 1682699807492552,
    "team": "opsml",
    "user_email": "user@email.com",
    "data_type": "DataFrame",
    "pipelinecard_uid": None,
}
```


## DataCard Args

`data`
: np.ndarray, pd.DataFrame, or pyarrow Table. You're data (Required)

`name`
: Name for the data (Required)

`team`
: Team data belongs to (Required)

`user_email`
: Email to associate with data (Required)

`sql_logic`
: SQL query or path to sql file containing logic to build data. Required if `data` is not provided.

`data_splits`
: Split logic for your data. Optional list of `DataSplit`.

`data_profile`
: `ydata-profiling` data profile. This can also be generated via `create_data_profile` method after instantiation.

`feature_descriptions`
: Dictionary contain feature descriptions (key -> feature name, value -> Description)

`additional_info`
: Dictionary used as storage object for extra information you'd like to provide.

## Data Splits

In most data science workflows, it's common to split data into different subsets for analysis and comparison. In support of this, `DataCard`s allow you to specify and split your data based on specific logic that is provided to a `DataSplit`.

### Split types

- **column name and value**: Split data based on a column value. Supports inequality signs. Works with `Pandas` and `Polars` `DataFrame`s.

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

- **indices**: Split data based on pre-defined indices.


## Data Profile

DataCards support [ydata-profiling](https://github.com/ydataai/ydata-profiling) reports out of the box. To add a data profile to your Datacard you can either supply a custom data profile created through the `ydata` library or you can call the `create_data_profile` method after `DataCard` instantiation.

### Example

```py
# Data
from sklearn.datasets import load_linnerud

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse


card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card = DataCard(info=card_info, data=data)

data_card.create_data_profile(sample_perc=0.5)  # you can specify a sampling percentage between 0 and 1

# if youd like to view you're report, you can export it to html or json
# Jupyter notebooks will render the html without needing to save (just call data_card.data_profile)
# data_card.data_profile.to_file("my_report.html")

# Registering card will automatically save the report and its html
data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)
```
*(Code will run as-is)*

### Comparing data profiles

You can also leverage `Opsml`'s thin profiling wrapper for comparing different data profiles


```py
from sklearn.datasets import load_linnerud
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard
from opsml.profile import DataProfiler

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Simulate creating 1st DataCard
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card = DataCard(info=card_info, data=data)
data_card.create_data_profile()

# Simulate creating 2nd DataCard
data2 = data * np.random.rand(data.shape[1])
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card2 = DataCard(info=card_info, data=data2)
data_card2.create_data_profile()

comparison = DataProfiler.compare_reports(reports=[data_card.data_profile, data_card2.data_profile])
comparison.to_file("comparison_report.html")
```
*(Code will run as-is)*

## Docs

::: opsml.registry.DataCard
    options:
        members:
            - create_data_profile
            - split_data
            - load_data
            - card_type
        show_root_heading: true
        show_source: true
        heading_level: 3
