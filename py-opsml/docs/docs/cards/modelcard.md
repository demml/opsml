
ModelCards help you store, version, and track model objects.

## Features
- **shareable**: All cards including ModelCards are shareable and searchable.
- **auto-schema**: Auto-infer data schema.
- **auto-metadata**: Extract model-specific metadata to associate with the card.
- **versioning**: Semver for your model. 
- **auto-onnx**: Optional automatic conversion of trained model into onnx model format.

## Create a Card

```python
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

# create data splits to store with the model (optional)
data_splits = [
    DataSplit(  # (1)
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

model_interface = SklearnModel( # (2)
    model=classifier,
    sample_data=X[0:10],
    task_type=TaskType.Classification,
)

model_interface.create_drift_profile(X)

modelcard = ModelCard( # (3)
    interface=model_interface,
    space="opsml",
    name="my_model",
    tags=["foo:bar", "baz:qux"],
    datacard_uid=datacard.uid,
)

# register model
reg.model.register_card(modelcard)
```

1. DataSplits allow you to create and store split logic with your DataInterface ensuring reproducibility
2. Here we are using the SklearnModel interface and passing in the trained model, sample data, and the task type
3. Here we are creating a ModelCard and passing in the model interface, space, name, tags, and the datacard_uid. The datacard_uid is used to link the model to the data it was trained on

## How it all works

As you can tell in the example above, `ModelCards` are created by passing in a `ModelInterface`, some required args and some optional args. The `ModelInterface` is the interface is a library-specific interface for saving and extracting metadata from the model. It also allows us to standardize how models are saved (by following the library's guidelines) and ensures reproducibility.

## Model Interface

The `ModelInterface` is the primary interface for working with models in `Opsml`. It is designed to be subclassed and can be used to store models in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `SklearnModel`: Stores data from a sklearn model
- `TorchModel`: Stores data from a pytorch model
- `LightningModel`: Stores data from a pytorch lightning model
- `HuggingFaceModel`: Stores data from a huggingface model
- `TensorFlowModel`: Stores data from a tensorflow model
- `XGBoostModel`: Stores data from a xgboost model
- `LightGBMModel`: Stores data from a lightgbm model
- `CatBoostModel`: Stores data from a catboost model

### Shared Arguments for all ModelInterfaces

- `model`: Model to save. See subclasses for supported model types
- `sample_data`: Sample of data that is fed to the model at inference time. As an example, if you are using a `SklearnModel` you would provide a numpy array at prediction time, so `sample_data` should be a numpy array for X features.
- `task_type`: Optional task type of the model. Defaults to `TaskType.Undefined`
- `drift_profile`: Optional `Scouter` drift profile to associated with model. This is a convenience argument if you already created a drift profile. You can also use interface.create_drift_profile(..) to create a drift profile from the model interface.



