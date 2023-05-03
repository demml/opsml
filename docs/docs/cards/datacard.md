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
from opsml.registry import CardInfo, DataCard, CardRegistry

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
        {"label": "train", "indices": train_idx},
        {"label": "test", "indices": test_idx},
    ],
)

# splits look good
splits = data_card.split_data()
print(splits.train.head())

"""   
    Chins  Situps  Jumps  Pulse
15   12.0   210.0  120.0   62.0
17   11.0   230.0   80.0   52.0
16    4.0    60.0   25.0   54.0
8    15.0   200.0   40.0   74.0
5     4.0   101.0   42.0   56.0
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

`data_splits`
: Split logic for your data. Optional list containing split logic. Defaults to None.

    Logic for data splits can be defined in the following three ways:

    You can specify as many splits as you'd like

    (1) Split based on column value (works for pd.DataFrame)

        splits = [
            {"label": "train", "column": "DF_COL", "column_value": 0}, -> "val" can also be a string
            {"label": "test",  "column": "DF_COL", "column_value": 1},
            {"label": "eval",  "column": "DF_COL", "column_value": 2},
            ]

    (2) Index slicing by start and stop (works for np.ndarray, pyarrow.Table, and pd.DataFrame)

        splits = [
            {"label": "train", "start": 0, "stop": 10},
            {"label": "test", "start": 11, "stop": 15},
            ]

    (3) Index slicing by list (works for np.ndarray, pyarrow.Table, and pd.DataFrame)

        splits = [
            {"label": "train", "indices": [1,2,3,4]},
            {"label": "test", "indices": [5,6,7,8]},
            ]

- **feature_descriptions**: Dictionary contain feature descriptions (key -> feature name, value -> Description)
- **additional_info**: Dictionary used as storage object for extra information you'd like to provide.


## Docs

::: opsml.registry.DataCard
    options:
        members:
            - split_data
            - load_data
            - card_type
        show_root_heading: true
        show_source: true
        heading_level: 3
