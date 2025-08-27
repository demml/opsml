from typing import Tuple, cast

import numpy as np
import pandas as pd
from opsml import CardRegistry, ModelCard, OnnxModel, RegistryType, TaskType
from opsml.helpers.data import create_fake_data
from skl2onnx import to_onnx  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore

model_registry = CardRegistry(registry_type=RegistryType.Model)


# create data
X_train, y_train = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

clr = RandomForestClassifier()
clr.fit(X_train.to_numpy(), y_train.to_numpy().ravel())

# Converting the model to ONNX
converted_model = to_onnx(clr, X_train.to_numpy()[:1])


interface = OnnxModel(
    model=converted_model,
    sample_data=X_train.to_numpy()[:1],
    task_type=TaskType.Classification,
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


## load card
loaded_modelcard: ModelCard = model_registry.load_card(uid=modelcard.uid)

## load card artifacts
loaded_modelcard.load()

assert loaded_modelcard.onnx_session is not None
assert loaded_modelcard.onnx_session.session is not None


# make predictions
input_name = loaded_modelcard.onnx_session.session.get_inputs()[0].name
label_name = loaded_modelcard.onnx_session.session.get_outputs()[0].name


pred_onx = loaded_modelcard.onnx_session.run(
    input_feed={input_name: X_train[0:10].to_numpy().astype(np.float64)},
    output_names=[label_name],
)[0]

print("Predictions: ", pred_onx)
