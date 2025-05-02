from opsml.helpers.data import create_fake_data
from typing import Tuple, cast
import pandas as pd
from opsml import (  # type: ignore
    SklearnModel,
    PandasData,
    CardRegistries,
    TaskType,
    DataCard,
    ModelCard,
)

from opsml.data import DataSplit, StartStopSplit
from sklearn import ensemble  # type: ignore


# start registries
reg = CardRegistries()

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))
X["target"] = y

# create data splits to store with the model
data_splits = [
    DataSplit(
        label="train",
        start_stop_split=StartStopSplit(
            start=0,
            stop=1000,
        ),
    ),
    DataSplit(
        label="test",
        start_stop_split=StartStopSplit(
            start=1000,
            stop=1200,
        ),
    ),
]

# create DataCard
datacard = DataCard(
    interface=PandasData(
        data=X,
        data_splits=data_splits,
        dependent_vars=["target"],
    ),
    space="opsml",
    name="my_data",
    tags=["foo:bar", "baz:qux"],
)

# register DataCard
reg.data.register_card(datacard)

splits = datacard.interface.split_data()

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(
    splits["train"].x.to_numpy(),
    splits["train"].y.to_numpy().ravel(),
)

model_interface = SklearnModel(
    model=classifier,
    sample_data=X[0:10],
    task_type=TaskType.Classification,
)

model_interface.create_drift_profile(X)

modelcard = ModelCard(
    interface=model_interface,
    space="opsml",
    name="my_model",
    tags=["foo:bar", "baz:qux"],
    datacard_uid=datacard.uid,
)

# register model
reg.model.register_card(modelcard)


# load model
loaded_modelcard = reg.model.load_card(uid=modelcard.uid)
loaded_modelcard.load()

assert loaded_modelcard.model is not None
