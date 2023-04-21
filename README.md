<h1 align="center">
  <br>
  <img src="images/opsml-logo.png"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h4 align="center">Tooling for machine learning workflows</h4>

<p align="center">
  <a href="https://drone.shipt.com/shipt/py-opsml">
  <img alt="Build Status" src="https://drone.shipt.com/api/badges/shipt/opsml-artifacts/status.svg"/>

  <a href="https://www.python.org/downloads/release/python-390/">
  <img alt="Python" src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Blue_Python_3.9_Shield_Badge.svg" />

  <img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="quality gate" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=alert_status&token=squ_06f8921843044242e5975ed012023f7b09066e9c"/>

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="coverage" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=coverage&token=squ_06f8921843044242e5975ed012023f7b09066e9c"/>
</p>

<h4 align="left">Supported Model Types</h4>

<a href="https://www.tensorflow.org/">
  <img alt="tensorflow" src="https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white"/>

<a href="https://keras.io/">
  <img alt="keras"" src="https://img.shields.io/badge/Keras-FF0000?logo=keras&logoColor=white"/>

<a href="https://pytorch.org/">
  <img alt="pytorch" src="https://img.shields.io/badge/PyTorch--EE4C2C.svg?style=flat&logo=pytorch"/>

<a href="https://scikit-learn.org/stable/">
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit_learn-F7931E?logo=scikit-learn&logoColor=white"/>


<a href="https://xgboost.readthedocs.io/en/stable/">
  <img alt="xgboost" src=https://img.shields.io/badge/Package-XGBoost-blueviolet"/>


<a href="https://lightgbm.readthedocs.io/en/v3.3.2/">
  <img alt="lightgbm" src=https://img.shields.io/badge/Package-LightGBM-success"/>

</p>

<p align="center">
  <a href="#what-is-it">What is it?</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#create-a-card">Create a Card</a> •
  <a href="#datacard">DataCard</a> •
  <a href="#modelcard">ModelCard</a> •
  <a href="#modelcard-predictor">ModelCard Predictor</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#contributing">Contributing</a> 
</p>

## What is it?

`OpsML` is a tooling library that simplifies the machine learning project lifecycle.

## Features:
  - **Simple Design**: Standardized design that can easily be incorporated into existing workflows.

  - **Cards**: Track, version, and store a variety of ML artifacts via cards (data, models, runs, pipelines) and a SQL-based card registry system. Think "trading cards for machine learning".

  - **Automation**: Automated processes including Onnx model conversion, api generation from Onnx model, data schema inference, code conversion and packaging for production.
  
  - **Pipelines**: Coming soon. Auto-pipeline creation

## Installation:
Before installing, you will need to set up your Artifactory credentials.

#### Request credentials for [Artifactory](https://techhub.shipt.com/engineering/infrastructure/devops/artifactory/) in Slack `#ask-info-sec`

Once you have your credentials, set the following variables.
```bash
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_USERNAME=your_username
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_PASSWORD=your_password
```

If using poetry, you must also add the following in your `pyproject.toml`
```toml
[[tool.poetry.source]]
name = "shipt-resolve"
url = "https://artifactory.shipt.com/artifactory/api/pypi/pypi-virtual/simple"
default = true
```

Next, add opsml to your environment
```bash
poetry add opsml
```
## Optional Dependencies
`Opsml` is designed to work with a variety of 3rd-party integrations depending on your use-case.

Types of extras that can be installed:

- **Postgres**: Installs postgres pyscopg2 dependency to be used with `Opsml`
  ```bash
  poetry add opsml[postgres]
  ```

- **Server**: Installs necessary packages for setting up an `Fastapi`/`Mlflow` based `Opsml` server
  ```bash
  poetry add opsml[server]
  ```

- **Mlflow**: Installs Mlflow for client-side interaction with an `Opsml` server
  ```bash
  poetry add opsml[mlflow]
  ```

- **GCP-mysql**: Installs mysql and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add opsml[gcp_mysql]
  ```

- **GCP-postgres**: Installs postgres and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add opsml[gcp_postgres]
  ```


## Getting Started
`Opsml` requires 1 or 2 environment variables depending on if you are using it as an all-in-one interface (no proxy) or you are using it as an interface to interact with an `Opsml` server (details on how to set up an `Opsml` server are below (TODO))
 
- **OPSML_TRACKING_URI**: **Required** This is the sql tracking uri to your card registry database. If interacting with an `Opsml` server, this will be the http address of the server. If this variable is not set, it will default to a local `SQLite` connection.

- **OPSML_STORAGE_URI**: **Optional** This is the storage uri to use for storing ml artifacts (models, data, figures, etc.). `Opsml` currently supports local file systems and google cloud storage.
If running `Opsml` as an all-in-one interfact, this variable is required and will default to a local folder if not specified. If interacting with an `Opsml` server, this variable does not need to be set.


## Cards
Cards (aka Artifact Cards) are one of the primary interfaces for working with `Opsml`.

Card Types:
- `DataCard`: Card used to store data-related information (data, dependent variables, feature descriptions, split logic, etc.)
- `ModelCard`: Card used to store trained model and model information
- `RunCard`: Stores artifact and metric info related to Data, Model, or Pipeline cards.
- `PipelineCard`: Stores information related to a training pipeline and all other cards created within the pipeline (Data, Run, Model)
- `ProjectCard`: Stores information related to unique projects. You will most likely never interact with this card directly.


<p align="center">
  <img src="images/card-flow.png"  width="457" height="332" alt="py opsml logo"/>
</p>


## Example (Creating Cards)

```python

import os
import numpy as np
from opsml.registry import DataCard, ModelCard, CardRegistry

# create some fake data
X_train = np.random.normal(-4, 2.0, size=(1000, 10))

col_names = []
for i in range(0, X_train.shape[1]):
    col_names.append(f"col_{i}")

X = pd.DataFrame(X_train, columns=col_names)
y = np.random.randint(1, 10, size=(1000, 1))

# Create a DataCard
# All of the following attributes are required
data_card = DataCard(
    data=X,
    name="linear-reg-data",
    team="opsml",
    user_email="user@email.com",
  )

# Register a card
# During registration a card is assigned a unique id and SemVer
data_registry = CardRegistry(registry_type="data")
data_registry.register_card(data_card)
print(data_card.version)
#> 1.0.0

# Create a ModelCard (and link it to data)
model_card = ModelCard(
    trained_model=reg,
    sample_input_data=X[0:1],
    name="linear_reg",
    team="mlops",
    user_email="user@email.com",
    datacard_uid=data_card.uid, # a ModelCard cannot be registered without linking it to a registered DataCard
    )
model_registry = CardRegistry(registry_type="model")
model_registry.register_card(model_card)   
```

## Creating A Run

```python

import os
import numpy as np
from opsml.projects import OpsmlProject, ProjectInfo

info = ProjectInfo(name="opsml-dev", team="opsml", user_email="user@email.com")
with opsml_project.run() as run:

  # create some fake data
  X_train = np.random.normal(-4, 2.0, size=(1000, 10))

  col_names = []
  for i in range(0, X_train.shape[1]):
      col_names.append(f"col_{i}")

  X = pd.DataFrame(X_train, columns=col_names)
  y = np.random.randint(1, 10, size=(1000, 1))

  # Create metrics / params / cards
  run.log_metric(key="m1", value=1.1)
  run.log_param(key="m1", value="apple")

  data_card = DataCard(
    data=X,
    name="linear-reg-data",
    team="opsml",
    user_email="user@email.com",
  )
  run.register_card(card=data_card, version_type="major") # you can specify "major", "minor", "patch"

  model_card = ModelCard(
    trained_model=reg,
    sample_input_data=X[0:1],
    name="linear_reg",
    team="mlops",
    user_email="user@email.com",
    datacard_uid=data_card.uid,
    )
  run.register_card(card=model_card)
```

## Contributing
- If you'd like to contribute, feel free to create a branch and start adding in your edits. If you'd like to work on any outstanding items, check out the `to_dos` directory readme and get started :smiley: