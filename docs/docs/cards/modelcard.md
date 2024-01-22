# Overview

ModelCards are cards for storing, versioning, and tracking model objects.

## Features
- **shareable**: All cards including ModelCards are shareable and searchable.
- **auto-onnx**: Automatic conversion of trained model into onnx model format.
- **auto-schema**: Auto-infer data schema and input and output signature.
- **versioning**: SemVer for your model.

## Create a Card

```python hl_lines="5 28 31-36"
# load data card from earlier
from sklearn.linear_model import LinearRegression

# Opsml
from opsml import CardRegistry, ModelCard, CardInfo

# set up registries
data_registry = CardRegistry(registry_name="data")
model_registry = CardRegistry(registry_name="model")

card_info = CardInfo(name="linnerrud", repository="opsml", contact="user@email.com")


# load datacard
datacard = data_registry.load_card(name=card_info.name, version="1.0.0")

# data is not loaded by default (helps when sharing cards with large data)
datacard.load_data()
data_splits = datacard.split_data()


X_train = data_splits.train.X
y_train = data_splits.train.y

# fit model
linreg = LinearRegression()
linreg = linreg.fit(X=X_train, y=y_train)
model_interface = SklearnModel(model=linreg, sample_data=X_train)

# lets test the onnx model before registering
modelcard = ModelCard(
    info=card_info,
    interface = model_interface,
    datacard_uid=datacard.uid,
    to_onnx=True,
)

# if you'd like to convert to onnx before registering, you can do that as well
modelcard.convert_to_onnx()

# custom onnx testing logic
...

# everything looks good
model_registry.register_card(modelcard)
```

## ModelCard Args

`name`: `str`
: Name for the data (Required)

`repository`: `str`
: repository data belongs to (Required)

`contact`: `str`
: Email to associate with data (Required)

`interface`: `ModelInterface`
: ModelInterface used to interact with model. See [ModelInterface](../interfaces/model/interfaces.md) for more information

`datacard_uid`
: uid of DataCard that contains training data. This is not required to instantiate a ModelCard, but it is required to register a ModelCard

`to_onnx`
: Whether to convert model to onnx or not. Default is True

`metadata`: `ModelCardMetadata`
: Optional ModelCardMetadata used to store metadata about the model. See [ModelCardMetadata](./metadata.md) for more information. If not provided, a default object is created. When registering a card, the metadata is updated with the latest information. 


---
## Docs

::: opsml.ModelCard
    options:
        members:
            - load_sample_data
            - load_trained_model
            - load_onnx_modelinition
            - onnx_model
        show_root_heading: true
        show_source: true
        heading_level: 3