# ModelCard

ModelCards are cards for storing, versioning, and tracking model objects.

## Features
- **shareable**: All cards including ModelCards are shareable and searchable.
- **auto-onnx**: Automatic conversion of trained model into onnx model format and associated onnx-model api definition. Currenlty supports `lightgbm`, `xgboost`, `sklearn` and most flavors of `Tensorflow`, `Pytorch` and `HuggingFace`.
- **auto-schema**: Auto-infer data schema and input and output signature.
- **versioning**: SemVer for your model.

## Create a Card

```python

# load data card from earlier
from sklearn.linear_model import LinearRegression

# Opsml
from opsml.registry import CardRegistry, ModelCard, CardInfo

# set up registries
data_registry = CardRegistry(registry_name="data")
model_registry = CardRegistry(registry_name="model")

card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")


# load datacard
datacard = data_registry.load_card(name=card_info.name, team=card_info.team, version="1.0.0")

# data is not loaded by default (helps when sharing cards with large data)
datacard.load_data()
data_splits = datacard.split_data()


X_train = data_splits.train
y_train = data_splits.train.pop(datacard.dependent_vars[0])

# fit model
linreg = LinearRegression()
linreg = linreg.fit(X=X_train, y=y_train)

# lets test the onnx model before registering
modelcard = ModelCard(
    info=card_info,
    trained_model=linreg,
    sample_input_data=X_train,
    datacard_uid=datacard.uid,
)

onnx_predictor = modelcard.onnx_model()
record = list(modelcard.sample_input_data[0:1].T.to_dict().values())[0]

pred_onnx = onnx_predictor.predict(record)[0].ravel()
pred_orig = onnx_predictor.predict_with_model(linreg, record)

print(f"Original: {pred_orig}, Onnx: {pred_onnx}")
# > Original: [54.4616866], Onnx: [54.4616866]

print(onnx_predictor.input_sig.schema_json())
print(onnx_predictor.output_sig.schema_json())

# everything looks good
model_registry.register_card(modelcard)

```
*(code requires DataCard to be registered. Refer to homepage example)*

Outputs 

```json
# input sig
{
    "title": "Features",
    "type": "object",
    "properties": {
        "Chins": {"title": "Chins", "type": "number"},
        "Situps": {"title": "Situps", "type": "number"},
        "Jumps": {"title": "Jumps", "type": "number"},
    },
    "required": ["Chins", "Situps", "Jumps"],
}

# output sig
{
    "title": "Features",
    "type": "object",
    "properties": {"variable": {"title": "Variable", "type": "number"}},
    "required": ["variable"],
}

```

## ModelCard Args

`trained_model`
: You're trained model (Required)

`sample_input_data`
: Sample of data used to train model (Required)

`name`
: Name for the model (Required)

`team`
: Team model belongs to (Required)

`user_email`
: Email to associate with model (Required)

`datacard_uid`
: uid of DataCard that contains training data. This is not required to instantiate a ModelCard, but it is required to register a ModelCard

## Docs

::: opsml.registry.ModelCard
    options:
        members:
            - load_sample_data
            - load_trained_model
            - load_onnx_model_definition
            - onnx_model
        show_root_heading: true
        show_source: true
        heading_level: 3