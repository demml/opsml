# Overview

DataCards are used for storing, versioning, and tracking data. All DataCards require a `DataInterface` and optional metadata. See [DataInterface](../interfaces/data/interfaces.md) for more information


## Creating a Card

```py hl_lines="6 19-27 29 45"
# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml import CardInfo, DataCard, CardRegistry, DataSplit, PandasData

card_info = CardInfo(name="linnerrud", repository="opsml", contact="user@email.com")
data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Split indices
indices = np.arange(data.shape[0])

# usual train-val split
train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

data_interface = PandasData(
    data=data,
    dependent_vars=["Pulse"],
    # define splits
    data_splits=[
        DataSplit(label="train", indices=train_idx),
        DataSplit(label="test", indices=test_idx),
    ],
)

data_card = DataCard(info=card_info, interface=data_interface)

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
```

## DataCard Args

`name`: `str`
: Name for the data (Required)

`repository`: `str`
: repository data belongs to (Required)

`contact`: `str`
: Email to associate with data (Required)

`interface`: `DataInterface`
: DataInterface used to interact with data. See [DataInterface](../interfaces/data/interfaces.md) for more information

`metadata`: `DataCardMetadata`
: Optional DataCardMetadata used to store metadata about data. See [DataCardMetadata](./data_metadata.md) for more information. If not provided, a default object is created. When registering a card, the metadata is updated with the latest information. 

---
## Docs

::: opsml.DataCard
    options:
        members:
            - create_data_profile
            - split_data
            - load_data
            - card_type
        show_root_heading: true
        show_source: true
        heading_level: 3
