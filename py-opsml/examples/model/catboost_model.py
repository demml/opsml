from opsml.helpers.data import create_fake_data
from typing import Tuple, cast
import pandas as pd
from opsml import (  # type: ignore
    CatBoostModel,
    CardRegistries,
    TaskType,
    ModelCard,
)
from catboost import CatBoostRegressor  # type: ignore


# start registries
registry = CardRegistries()

# create data
X_train, y_train = cast(
    Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200)
)

model = CatBoostRegressor(n_estimators=5, max_depth=3)
model.fit(X_train.to_numpy(), y_train)

model_interface = CatBoostModel(
    model=model,
    sample_data=X_train[0:10],
    task_type=TaskType.Regression,
)

model_interface.create_drift_profile(X_train)
modelcard = ModelCard(interface=model_interface, space="opsml", name="my_model")

# register model
registry.model.register_card(modelcard)


# load model
loaded_modelcard: ModelCard = registry.model.load_card(uid=modelcard.uid)
loaded_modelcard.load()

assert loaded_modelcard.model is not None
