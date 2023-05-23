# Data and Model
from sklearn.datasets import load_linnerud
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, ModelCard

# set up registries
data_registry = CardRegistry(registry_name="data")
model_registry = CardRegistry(registry_name="model")

# card info (optional, but is used to simplify required args a bit)
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")

# get X, y
data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Split indices
indices = np.arange(data.shape[0])

# usual train-test split
train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

datacard = DataCard(
    info=card_info,
    data=data,
    dependent_vars=["Pulse"],
    # define splits
    data_splits=[
        {"label": "train", "indices": train_idx},
        {"label": "test", "indices": test_idx},
    ],
)

# register card
data_registry.register_card(datacard)

# split data
data_splits = datacard.split_data()
X_train = data_splits.train
y_train = data_splits.train.pop(datacard.dependent_vars[0])

# fit model
linreg = LinearRegression()
linreg = linreg.fit(X=X_train, y=y_train)

# Create ModelCard
modelcard = ModelCard(
    info=card_info,
    trained_model=linreg,
    sample_input_data=X_train,
    datacard_uid=datacard.uid,
)

model_registry.register_card(card=modelcard)

# >{"level": "INFO", "message": "OPSML_DATA_REGISTRY: linnerrud, version:1.0.0 registered", "timestamp": "2023-04-27T19:12:30", "app_env": "development"}
# >{"level": "INFO", "message": "Validating converted onnx model", "timestamp": "2023-04-27T19:12:30", "app_env": "development"}
# >{"level": "INFO", "message": "Onnx model validated", "timestamp": "2023-04-27T19:12:30", "app_env": "development"}
# >{"level": "INFO", "message": "OPSML_MODEL_REGISTRY: linnerrud, version:1.0.0 registered", "timestamp": "2023-04-27T19:12:30", "app_env": "development"}


print(data_registry.list_cards(info=card_info, as_dataframe=False))
"""
[
    {
        "timestamp": 1682622948626806,
        "name": "linnerrud",
        "version": "1.0.0",
        "data_uri": "/opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.0.0/linnerrud.parquet",
        "runcard_uid": None,
        "datacard_uri": "/opsml_artifacts/OPSML_DATA_REGISTRY/opsml/linnerrud/v-1.0.0/datacard.joblib",
        "app_env": "development",
        "uid": "873978bf4c3a49be819b9813f8d02ae8",
        "date": "2023-04-27",
        "team": "opsml",
        "user_email": "user@email.com",
        "data_type": "DataFrame",
        "pipelinecard_uid": None,
    }
]
"""

print(model_registry.list_cards(info=card_info, as_dataframe=False))

"""
[
    {
        "uid": "3fa6f762c5b74d4289b1e52bfd66f158",
        "app_env": "development",
        "team": "opsml",
        "user_email": "user@email.com",
        "datacard_uid": "873978bf4c3a49be819b9813f8d02ae8",
        "onnx_model_uri": "/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/api-def.json",
        "sample_data_type": "DataFrame",
        "runcard_uid": None,
        "timestamp": 1682622948628464,
        "date": "2023-04-27",
        "name": "linnerrud",
        "version": "1.0.0",
        "modelcard_uri": "opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/modelcard.joblib",
        "trained_model_uri": "/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/trained-model.joblib",
        "sample_data_uri": "/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/sample-model-data.parquet",
        "model_type": "sklearn_estimator",
        "pipelinecard_uid": None,
    }
]
"""
