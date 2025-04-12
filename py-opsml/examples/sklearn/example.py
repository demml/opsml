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
    ModelCardMetadata,
)
from sklearn import ensemble  # type: ignore


# start registries
reg = CardRegistries()

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

# create DataCard
datacard = DataCard(
    interface=PandasData(data=X),
    space="opsml",
    name="my_data",
    tags=["foo:bar", "baz:qux"],
)

# register DataCard
reg.data.register_card(datacard)

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X.to_numpy(), y.to_numpy().ravel())

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
    to_onnx=True,  # aut-convert to onnx (optional)
    tags=["foo:bar", "baz:qux"],
    metadata=ModelCardMetadata(
        datacard_uid=datacard.uid,  # link to datacard (optional)
    ),
)

# register model
reg.model.register_card(modelcard)

print(modelcard)
