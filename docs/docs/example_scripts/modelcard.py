from sklearn.linear_model import LinearRegression

# Opsml
from opsml.registry import CardRegistry, ModelCard, CardInfo

# set up registries
data_registry = CardRegistry(registry_name="data")
model_registry = CardRegistry(registry_name="model")

card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")


# load datacard
datacard = data_registry.load_card(name=card_info.name, version="1.0.0")

# data is not loaded by default
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

print(onnx_predictor.input_sig.model_json_schema())

"""
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
"""


print(onnx_predictor.output_sig.schema_json())

"""
{
    "title": "Features",
    "type": "object",
    "properties": {"variable": {"title": "Variable", "type": "number"}},
    "required": ["variable"],
}
"""
# everything looks good
model_registry.register_card(modelcard)
