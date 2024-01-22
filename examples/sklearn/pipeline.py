import numpy as np
from sklearn import ensemble
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    ModelCard,
    PandasData,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data

""""This example walks through creating an Sklearn pipelines featuring and ColumnTransformer and a stacking regressor

Steps:
    - Create data and datacard
    - Instantiate ColumnTransformer and Pipeline with StackingRegressor
    - Create model interface and modelcard
    - Load trained model and test onnx predictions
"""

"""-------------------------------------DataCard-------------------------------------"""
info = CardInfo(name="sklearn_pipeline", repository="opsml", contact="user@email.com")
registries = CardRegistries()

X, y = create_fake_data(n_samples=1000, n_categorical_features=2, task_type="regression")
X["target"] = y

# Create data interface
data_interface = PandasData(
    data=X,
    data_splits=[
        DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
        DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
    ],
    dependent_vars=["target"],
)

# Create datacard
datacard = DataCard(interface=data_interface, info=info)
registries.data.register_card(card=datacard)

"""-------------------------------------ModelCard-------------------------------------"""

# setup columntransformer
cat_cols = ["cat_col_0", "cat_col_1"]
categorical_transformer = Pipeline([("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))])
preprocessor = ColumnTransformer(
    transformers=[("cat", categorical_transformer, cat_cols)],
    remainder="passthrough",
)

# setup stacking regressor
estimators = [
    ("lr", ensemble.RandomForestRegressor(n_estimators=5)),
    ("lin", LinearRegression()),
]
stack = ensemble.StackingRegressor(
    estimators=estimators,
    final_estimator=ensemble.RandomForestRegressor(n_estimators=5, random_state=42),
    cv=2,
)

# build pipeline
pipe = Pipeline([("preprocess", preprocessor), ("stacking", stack)])

# split data
data = datacard.split_data()

# fit
pipe.fit(data.train.X, data.train.y)

# create model interface
interface = SklearnModel(
    model=pipe,
    sample_data=data.train.X,
    task_type="regression",  # optional
)

# create modelcard
modelcard = ModelCard(interface=interface, info=info, datacard_uid=datacard.uid, to_onnx=True)
registries.model.register_card(card=modelcard)

"""-------------------------------------Onnx-------------------------------------"""

inputs = {}
for c in data.test.X.columns:
    values = data.test.X[c][:1].values
    if c in cat_cols:
        values = values.astype(str).reshape(-1, 1)
    else:
        values = values.astype(np.float32).reshape(-1, 1)
    inputs[c] = values

print(modelcard.onnx_model.sess.run(None, inputs))
