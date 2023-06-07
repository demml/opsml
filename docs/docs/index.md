<p align="center">
  <img src="images/opsml-logo.png"  width="400" height="400" alt="opsml logo"/>
</p>

<h4 align="center">Tooling for machine learning workflows</h4>
---
<p align="center">
  <a href="https://drone.shipt.com/shipt/opsml">
  <img alt="Build Status" src="https://drone.shipt.com/api/badges/shipt/opsml/status.svg"/>
  </a>

  <a href="https://www.python.org/downloads/release/python-390/">
  <img alt="Python" src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Blue_Python_3.9_Shield_Badge.svg" />
  </a>

  <img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="quality gate" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=alert_status&token=squ_06f8921843044242e5975ed012023f7b09066e9c"/>
  </a>

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="coverage" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=coverage&token=squ_06f8921843044242e5975ed012023f7b09066e9c"/>
  </a>
</p>

<h4 align="left">Supported Model Types</h4>

<p align="center">

<a href="https://www.tensorflow.org/">
  <img alt="tensorflow" src="https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white"/>
</a>

<a href="https://keras.io/">
  <img alt="keras"" src="https://img.shields.io/badge/Keras-FF0000?logo=keras&logoColor=white"/>
</a>

<a href="https://pytorch.org/">
  <img alt="pytorch" src="https://img.shields.io/badge/PyTorch--EE4C2C.svg?style=flat&logo=pytorch"/>
</a>

<a href="https://scikit-learn.org/stable/">
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit_learn-F7931E?logo=scikit-learn&logoColor=white"/>
</a>

<a href="https://xgboost.readthedocs.io/en/stable/">
  <img alt="xgboost" src=https://img.shields.io/badge/Package-XGBoost-blueviolet"/>
</a>

<a href="https://lightgbm.readthedocs.io/en/v3.3.2/">
  <img alt="lightgbm" src=https://img.shields.io/badge/Package-LightGBM-success">
</a>

<a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="coverage" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=coverage&token=squ_06f8921843044242e5975ed012023f7b09066e9c">

</a>
</p>


**Source Code**: [Code](https://github.com/shipt/opsml)

## What is it?

`OpsML` is a tooling library that simplifies the machine learning project lifecycle.

## Features

  - `Shareable`: Share cards and workflows across teams
  
  - `Simple Design`: Standardized design that can easily be incorporated into existing workflows.

  - `Cards`: Track, version, and store a variety of ML artifacts via cards (data, models, runs, pipelines) and a SQL-based card registry system. Think "trading cards for machine learning".

  - `Automation`: Automated processes including Onnx model conversion, api generation from Onnx model, data schema inference, code conversion and packaging for production.
  
  - `Pipelines`: Coming soon. Auto-pipeline creation

## Why?

The main goal of `Opsml` is to provide an intuitive interface for DSs to create standardized, resuable and auditable machine learning workflows.

### Two sides of the same coin (dev as prod)

Taking a data science project from ideation :bulb: to deployment :rocket: often involves a `dev` side and a `deployment` side. 

#### Dev Themes

- Experimentation and iteration in order to generate many potential solutions
- Feature/Data engineering
- Algorithm development
- Felxible work environment (often **Jupyter Notebooks**)
- Many other things

#### Deployment Themes

- Compute infrastructure for hosting
- Conversion of data science code to production code (including creating dags/pipelines)
- CI/CD
- Versioning
- Monitoring
- Security

#### Resulting Pain Points

- :angry: Overhead in packaging data science code into production code. This results in duplicating data science code just to run in another environment (necessary, but can this be simplified?). 

- :watch: Time lag in deployment due to different teams having different priorities (especially true if developers/ML engineers are needed to help data scientists deploy their code)

- :rage: Inflexible prod code that is not easily updatable

- :sob: Often no linking of metadata across the entire workflow (data, runs/experiments, models, pipelines)

What `Opsml` aims to do is provide an interface into both sides and simplify the entire workflow experience by removing non-value added time from `dev` and `deployment` processes and help teams go from ideation to deployment quicker :smile: with the added benefits of reproducibility and auditability.


## Example

The primary interface for `Opsml` is an `ArtifactCard` (see [here](cards/overview.md) for detailed information). All Cards within `Opsml` follow the same design with a few specific required arguments for each card type. The following example shows how to create a DataCard and a ModelCard.

```python
# Data and Model
from sklearn.datasets import load_linnerud
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, ModelCard, DataSplit

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
        DataSplit(label="train", indices=train_idx),
        DataSplit(label="test", indices=test_idx),
    ],
)

# register card
data_registry.register_card(datacard)

# split data
data_splits = datacard.split_data()
X_train = data_splits.train.X
y_train = data_splits.train.y

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
print(model_registry.list_cards(info=card_info, as_dataframe=False))
```
*(Code will run as-is)*

Outputs:

```json
# data registry output
[
    {
        "uid": "3fa6f762c5b74d4289b1e52bfd66f158",
        "app_env": "development",
        "team": "opsml",
        "user_email": "user@email.com",
        "datacard_uid": "873978bf4c3a49be819b9813f8d02ae8",
        "onnx_model_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/api-def.json",
        "sample_data_type": "DataFrame",
        "runcard_uid": None,
        "timestamp": 1682622948628464,
        "date": "2023-04-27",
        "name": "linnerrud",
        "version": "1.0.0",
        "modelcard_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/modelcard.joblib",
        "trained_model_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/trained-model.joblib",
        "sample_data_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/sample-model-data.parquet",
        "model_type": "sklearn_estimator",
        "pipelinecard_uid": None,
    }
]

# model registry output
[
    {
        "uid": "3fa6f762c5b74d4289b1e52bfd66f158",
        "app_env": "development",
        "team": "opsml",
        "user_email": "user@email.com",
        "datacard_uid": "873978bf4c3a49be819b9813f8d02ae8",
        "onnx_model_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/api-def.json",
        "sample_data_type": "DataFrame",
        "runcard_uid": None,
        "timestamp": 1682622948628464,
        "date": "2023-04-27",
        "name": "linnerrud",
        "version": "1.0.0",
        "modelcard_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/modelcard.joblib",
        "trained_model_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/trained-model.joblib",
        "sample_data_uri": "/***/***/opsml_artifacts/OPSML_MODEL_REGISTRY/opsml/linnerrud/v-1.0.0/sample-model-data.parquet",
        "model_type": "sklearn_estimator",
        "pipelinecard_uid": None,
    }
]
```
