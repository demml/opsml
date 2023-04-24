from sklearn.datasets import load_iris
import pandas as pd
import numpy as np
from opsml.registry import DataCard, CardRegistry

data = load_iris()

df = pd.DataFrame(data=data.data, columns=data.feature_names)
df["target"] = data.target

# generic splits
train_indices = np.arange(0, 100)
test_indices = np.arange(100, 150)


DATA_SPLITS = [
    {"label": "train", "indices": train_indices},
    {"label": "test", "indices": test_indices},
]

# Create DataCard
data_card = DataCard(
    data=df,
    name="iris-data",
    team="opsml",
    user_email="user@email.com",
    data_splits=DATA_SPLITS,
    dependent_vars=["target"],
)

data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)


# load the card
loaded_card = data_registry.load_card(uid=data_card.uid)

print(loaded_card.version)
# > 1.0.0

# loaded cards do not load data by default
loaded_card.load_data()
print(type(loaded_card.data))
# > <class 'pandas.core.frame.DataFrame'>
