import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889/"

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
        DataSplit(label="train", indices=train_idx),
        DataSplit(label="test", indices=test_idx),
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
cards = data_registry.list_cards(uid=data_card.uid, as_dataframe=False)  # can also supply, name, team, version
print(cards[0])

"""
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
"""
# code will run as-is
