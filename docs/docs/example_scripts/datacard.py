import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889"

# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse


# Split indices
indices = np.arange(700000)

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
# splits = data_card.split_data()
# print(splits.train.head())

"""   
    Chins  Situps  Jumps  Pulse
18   15.0   225.0   73.0   54.0
10   17.0   120.0   38.0   50.0
14    6.0    70.0   31.0   46.0
19    2.0   110.0   43.0   68.0
12   14.0   215.0  105.0   64.0
"""

data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)
print(data_card.version)
# > 1.0.0

# list cards
cards = data_registry.list_cards(uid=data_card.uid, as_dataframe=False)  # can also supply, name, team, version
print(cards[0])

"""
{
    "timestamp": 1682472648928559,
    "name": "linnerrud",
    "version": "1.2.0",
    "data_uri": "opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.2.0/linnerrud.parquet",
    "feature_descriptions": None,
    "data_type": "DataFrame",
    "dependent_vars": ["Pulse"],
    "pipelinecard_uid": None,
    "date": "2023-04-26",
    "uid": "38da1aaecfac42048cbde821a55289ab",
    "app_env": "development",
    "team": "opsml",
    "user_email": "user@email.com",
    "feature_map": {"Chins": "double", "Situps": "double", "Jumps": "double", "Pulse": "double"},
    "data_splits": {
        "splits": [
            {"label": "train", "indices": [9, 8, 11, 2, 6, 12, 14, 1, 7, 4, 13, 19, 16, 17, 15, 10]},
            {"label": "test", "indices": [18, 5, 3, 0]},
        ]
    },
    "additional_info": {},
    "runcard_uid": None,
    "datacard_uri": "opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.2.0/datacard.joblib",
}
"""
# code will run as-is
