<p align="center">
  <img src="images/opsml-logo.png"  width="400" height="400" alt="opsml logo"/>
</p>

<h4 align="center">Tooling for machine learning workflows</h4>
---

[![Tests](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml/badge.svg?branch=main)](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)

<h4 align="left">Supported Model Types</h4>

[![Keras](https://img.shields.io/badge/Keras-FF0000?logo=keras&logoColor=white)]()
[![Pytorch](https://img.shields.io/badge/PyTorch--EE4C2C.svg?style=flat&logo=pytorch)]()
[![Sklearn](https://img.shields.io/badge/scikit_learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/stable/)
[![Xgboost](https://img.shields.io/badge/Package-XGBoost-blueviolet)](https://xgboost.readthedocs.io/en/stable/)
[![Lightgbm](https://img.shields.io/badge/Package-LightGBM-success)](https://lightgbm.readthedocs.io/en/v3.3.2/)


<h4 align="left">Supported Storage Types</h4>

[![GCS](https://img.shields.io/badge/google_cloud_storage-grey.svg?logo=google-cloud)](https://cloud.google.com/storage)
[![S3](https://img.shields.io/badge/aws_s3-grey?logo=amazons3)](https://aws.amazon.com/)


**Source Code**: [Code](https://github.com/shipt/opsml)

## What is it?

`OpsML` is an ML tooling library that simplifies the machine learning project lifecycle and provides process consistency.

## Why?

The end-result of a machine learning project is often an artifact that is used as a component in a production process. Because of this, ML artifacts must conform to and meet engineering specifications in order to provide businesses with service guarantees and customers with a consistent experience. Thus, the creation and use of ML artifacts is no different than a manufacturing process. With this in mind, `OpsML` aims to help DS and Eng teams by providing consistency and standardization across the entire ML workflow in the production of ML artifacts.

## Features
  
  - `Simple Design`: Standardized design that can easily be incorporated into existing workflows.

  - `Cards`: Track, version, and store a variety of ML artifacts via `cards`` (data, models, runs, projects) and a SQL-based card registry system. Think **"trading cards for machine learning"**.

  - `Prioritization`: Every `Card` is given the same priority. No more treating `data` as a model artifact.

  - `Automation`: Automated processes including Onnx model conversion, data schema inference, code conversion and packaging for production.

  - `Consistency`: No surpises. Outputs and generated artifacts follow engineering standards providing consistency across the entire ML workflow. `Varying input --> Standardized output`.

  - `Shareable`: Share cards and workflows across teams

  - `Server`: Run `Opsml` as a server to provide a centralized location for ML artifacts and metadata. Easily setup on any system that supports Docker.


### Two sides of the same coin (dev as prod)

Taking a data science project from ideation :bulb: to deployment :rocket: often involves a `development` side and a `production` side. 

#### Development Themes

- Experimentation and iteration in order to generate many potential solutions
- Feature/Data engineering
- Algorithm development
- Flexible work environment (often **Jupyter Notebooks**)
- Many other things

#### Production Themes

- Compute infrastructure for hosting
- Conversion of data science code to production code (data/model artifacts, metadata, etc.)
- CI/CD
- Versioning
- Monitoring
- Security

#### Resulting Pain Points

- :angry: Overhead in packaging data science code into production code. This results in duplicating data science code just to run in another environment (necessary, but can this be simplified?). 

- :watch: Time lag in deployment due to different teams having different priorities (especially true if developers/ML engineers are needed to help data scientists deploy their code). Lack of consistency in the production process.

- :rage: Inflexible prod code that is not easily updatable

- :sob: Often no linking of metadata across the entire workflow (data, runs/experiments, models, pipelines)

What `Opsml` aims to do is provide an interface into both sides and simplify the entire workflow experience by removing non-value added time from `development` and `production` processes and help teams go from ideation to deployment quicker :smile: with the added benefits of reproducibility and auditability.

## Why Use OpsML vs other open source or vendor tooling?

With the plethora of available ML tooling it can be difficult to decide which tooling to use. The following are some reasons why you might want to use `Opsml` and why we created it.

- Need for a consistent and standardized ML workflow to use in your organization
- Not enthusiastic about vendor lock-in or paying a vendor to use an SDK and UI but still need to create and maintain your own infrastructure
- You want to use a tool that is open source and continually developed
- You want all artifacts to be given the same priority (no more treating data as less of a priority than models)
- Don't want to worry about implementation details (how to version, store and track artifacts)
- You'd like to have auto-generated metadata that meets engineering standards and can be used in production
- You want to be able to share artifacts and workflows across teams

## Example

The primary interface for `Opsml` is an `ArtifactCard` (see [here](cards/overview.md) for detailed information). All Cards within `Opsml` follow the same design with a few specific required arguments for each card type. The following example shows how to create a `DataCard` and a `ModelCard`.

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

data registry output
```json
[
    {
        "name": "linnerrud",
        "version": "1.0.0",
        "tags": {},
        "data_type": "PandasDataFrame",
        "pipelinecard_uid": null,
        "date": "2023-10-29",
        "timestamp": 1698622188318014,
        "app_env": "development",
        "uid": "07131023c60d4a6892092851eab0f86d",
        "team": "opsml",
        "user_email": "user@email.com",
        "data_uri": "***/OPSML_DATA_REGISTRY/opsml/linnerrud/v1.0.0/linnerrud.parquet",
        "runcard_uid": null,
        "datacard_uri": "***/OPSML_DATA_REGISTRY/opsml/linnerrud/v1.0.0/datacard.joblib",
    }

]
```

model registry output
```json
[
    {
        "uid": "1e68ef7851b34974bfaac764f348491d",
        "app_env": "development",
        "team": "opsml",
        "user_email": "user@email.com",
        "modelcard_uri": "***//OPSML_MODEL_REGISTRY/opsml/linnerrud/v1.0.0/modelcard.joblib",
        "trained_model_uri": "***//OPSML_MODEL_REGISTRY/opsml/linnerrud/v1.0.0/model/trained-model.joblib",
        "sample_data_uri": "***//OPSML_MODEL_REGISTRY/opsml/linnerrud/v1.0.0/sample-model-data.parquet",
        "model_type": "sklearn_estimator",
        "pipelinecard_uid": null,
        "date": "2023-10-29",
        "name": "linnerrud",
        "timestamp": 1698622188320834,
        "version": "1.0.0",
        "tags": {},
        "datacard_uid": "07131023c60d4a6892092851eab0f86d",
        "model_metadata_uri": "***/OPSML_MODEL_REGISTRY/opsml/linnerrud/v1.0.0/model-metadata.json",
        "sample_data_type": "PandasDataFrame",
        "runcard_uid": null,
    }
]
```
