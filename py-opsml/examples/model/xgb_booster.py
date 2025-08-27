from typing import Tuple, cast

import pandas as pd
import xgboost as xgb
from opsml import CardRegistry, ModelCard, RegistryType, TaskType, XGBoostModel
from opsml.helpers.data import create_fake_data

model_registry = CardRegistry(registry_type=RegistryType.Model)


# create data
X_train, y_train = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

dtrain = xgb.DMatrix(X_train.to_numpy(), y_train.to_numpy())
dtest = xgb.DMatrix(X_train[0:10].to_numpy(), y_train[0:10].to_numpy())

param = {"max_depth": 2, "eta": 1, "objective": "reg:tweedie"}
# specify validations set to watch performance
watchlist = [(dtest, "eval"), (dtrain, "train")]

# number of boosting rounds
num_round = 2
bst = xgb.train(param, dtrain, num_boost_round=num_round, evals=watchlist)


interface = XGBoostModel(
    model=bst,
    sample_data=dtrain,
    task_type=TaskType.Regression,
)

# create ModelCard
modelcard = ModelCard(
    interface=interface,
    space="opsml",
    name="my_model",
)

# register ModelCard
model_registry.register_card(modelcard)


# list card
model_registry.list_cards(uid=modelcard.uid).as_table()


# load card
loaded_modelcard: ModelCard = model_registry.load_card(uid=modelcard.uid)

# load card artifacts
loaded_modelcard.load()

assert loaded_modelcard.model is not None
