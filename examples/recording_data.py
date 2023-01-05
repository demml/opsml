from opsml_data import DataCard, DataRegistry
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Instantiate data registry
registry = DataRegistry()

#################### Create pandas dataframe with index list for splitting data ########
# create fake data
mu_1, mu_2 = -4, 4
X_data = np.random.normal(mu_1, 2.0, size=(1000, 10))
y_data = np.random.randint(2, 100, size=(1000, 1))

col_names = []
for i in range(0, X_data.shape[1]):
    col_names.append(f"col_{i}")

data = pd.DataFrame(X_data, columns=col_names)
data["target"] = y_data

# get split indices
train_idx, test_idx = train_test_split(np.arange(data.shape[0]), test_size=0.3)
print(train_idx)
