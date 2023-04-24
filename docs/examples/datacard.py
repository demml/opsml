# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard

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
18   15.0   225.0   73.0   54.0
10   17.0   120.0   38.0   50.0
14    6.0    70.0   31.0   46.0
19    2.0   110.0   43.0   68.0
12   14.0   215.0  105.0   64.0
"""
