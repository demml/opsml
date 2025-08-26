from typing import Tuple, cast

import lightgbm as lgb
import pandas as pd
from opsml import CardRegistry, LightGBMModel, ModelCard, RegistryType, TaskType
from opsml.helpers.data import create_fake_data
from opsml.logging import LoggingConfig, LogLevel, RustyLogger

logger = RustyLogger.get_logger(
    config=LoggingConfig(log_level=LogLevel.Info),
)

logger.info("Starting the model card example...")
model_registry = CardRegistry(registry_type=RegistryType.Model)


# create data
X_train, y_train = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))


# create dataset for lightgbm
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_train[0:10], y_train[0:10], reference=lgb_train)
# specify your configurations as a dict

params = {
    "boosting_type": "gbdt",
    "objective": "regression",
    "metric": {"l2", "l1"},
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": 0,
}
# train
gbm = lgb.train(
    params,
    lgb_train,
    num_boost_round=20,
    valid_sets=[lgb_eval],
    callbacks=[
        lgb.early_stopping(stopping_rounds=5),
    ],
)

interface = LightGBMModel(
    model=gbm,
    sample_data=X_train[0:10],
    task_type=TaskType.Regression,
)

# create ModelCard
modelcard = ModelCard(
    interface=interface,
    space="opsml",
    name="my_model",
)

logger.info("Registering the model card...")
model_registry.register_card(modelcard)


logger.info("Listing the model card...")
model_registry.list_cards(uid=modelcard.uid).as_table()

logger.info("Loading the model card...")
loaded_modelcard: ModelCard = model_registry.load_card(uid=modelcard.uid)

# load card artifacts
loaded_modelcard.load()

assert loaded_modelcard.model is not None
