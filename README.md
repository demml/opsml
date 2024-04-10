<h1 align="center">
  <br>
  <img src="https://github.com/shipt/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>


<h2 align="center">Universal Artifact Registration System for Machine Learning</h2>

<h1 align="center"><a href="https://thorrester.github.io/opsml-ghpages/">OpsML Documentation</h1>

[![Tests](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml/badge.svg?branch=main)](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml)
[![Examples](https://github.com/shipt/opsml/actions/workflows/examples.yml/badge.svg)](https://github.com/shipt/opsml/actions/workflows/examples.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)


## What is it?

`OpsML` provides tooling that enables data science and engineering teams to better govern and manage their machine learning projects and artifacts by providing a standardized and universal registration system and repeatable patterns for tracking, versioning and storing ML artifacts.


## Features:
  - **Simple Design**: Standardized design that can easily be incorporated into existing projects.

  - **Cards**: Track, version and store a variety of ML artifacts via cards (data, models, runs, projects) and a SQL-based card registry system. Think `trading cards for machine learning`.

  - **Type Checking**: Strongly typed and type checking for data and model artifacts.

  - **Support**: Robust support for a variety of ML and data libraries.

  - **Automation**: Automated processes including onnx model conversion, metadata creation and production packaging.


## Incorporate into Existing Workflows

Add quality control to your ML projects with little effort! With `opsml`, data and models are added to interfaces and cards, which are then registered via card registries. 

# Incorporate into Existing Workflows

Given its simple and modular design, `opsml` can be easily incorporated into existing workflows. 

<h1 align="center">
  <br>
  <img src="https://github.com/shipt/opsml/blob/main/images/opsml-chip.png?raw=true"  width="800" alt="opsml logo"/>
  <br>
</h1>


## Installation:

### Poetry

```bash
poetry add opsml
```

### Pip

```bash
pip install opsml
```

Setup your local environment:

By default, `opsml` will log artifacts and experiments locally. To change this behavior and log to a remote server, you'll need to set the following environment variables:

```shell
export OPSML_TRACKING_URI=${YOUR_TRACKING_URI}
```

## Quickstart

If running the example below locally without a server, make sure to install the `server` extra:

```bash 
poetry add "opsml[server]"
```

```python
# imports
from sklearn.linear_model import LinearRegression
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


info = CardInfo(name="linear-regression", repository="opsml", user_email="user@email.com")
registries = CardRegistries()


#--------- Create DataCard ---------#

# create fake data
X, y = create_fake_data(n_samples=1000, task_type="regression")
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

# Create and register datacard
datacard = DataCard(interface=data_interface, info=info)
registries.data.register_card(card=datacard)

#--------- Create ModelCard ---------#

# split data
data = datacard.split_data()

# fit model
reg = LinearRegression()
reg.fit(data["train"].X.to_numpy(), data["train"].y.to_numpy())

# create model interface
interface = SklearnModel(
    model=reg,
    sample_data=data["train"].X.to_numpy(),
    task_type="regression",  # optional
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True,  # lets convert onnx
    datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
)
registries.model.register_card(card=modelcard)
```

## Table of Contents
- [Incorporate into Existing Workflows](#incorporate-into-existing-workflows-1)
  - [Installation:](#installation)
    - [Poetry](#poetry)
    - [Pip](#pip)
  - [Quickstart](#quickstart)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
  - [Advanced Installation Scenarios](#advanced-installation-scenarios)
  - [Environment Variables](#environment-variables)
- [Supported Libraries](#supported-libraries)
  - [Data Libraries](#data-libraries)
  - [Model Libraries](#model-libraries)
  - [Contributing](#contributing)

## Usage

Now that `opsml` is installed, you're ready to start using it!

It's time to point you to the official [Documentation Website](https://thorrester.github.io/opsml-ghpages/) for more information on how to use `opsml`


## Advanced Installation Scenarios

`Opsml` is designed to work with a variety of 3rd-party integrations depending on your use-case.

Types of extras that can be installed:

- **Postgres**: Installs postgres pyscopg2 dependency to be used with `Opsml`
  ```bash
  poetry add "opsml[postgres]"
  ```

- **Server**: Installs necessary packages for setting up a `Fastapi`-based `Opsml` server
  ```bash
  poetry add "opsml[server]"
  ```

- **GCP with mysql**: Installs mysql and gcsfs to be used with `Opsml`
  ```bash
  poetry add "opsml[gcs,mysql]"
  ```

- **GCP with mysql(cloud-sql)**: Installs mysql and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_mysql]"
  ```

- **GCP with postgres**: Installs postgres and gcsgs to be used with `Opsml`
  ```bash
  poetry add "opsml[gcs,postgres]"
  ```

- **GCP with postgres(cloud-sql)**: Installs postgres and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_postgres]"
  ```

- **AWS with postgres**: Installs postgres and s3fs dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[s3,postgres]"
  ```

- **AWS with mysql**: Installs mysql and s3fs dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[s3,mysql]"
  ```

## Environment Variables

The following environment variables are used to configure opsml. When using
opsml as a client (i.e., not running a server), the only variable that must be
set is `OPSML_TRACKING_URI`.

| Name                       | Description                                                                                                                     |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| APP_ENV                    | The environment to use. Supports `development`, `staging`, and `production`                                                      |
| GOOGLE_ACCOUNT_JSON_BASE64 | The base64 string of the the GCP service account to use.                                                                        |
| OPSML_MAX_OVERFLOW         | The SQL "max_overflow" size. Defaults to 5                                                                                      |
| OPSML_POOL_SIZE            | The SQL connection pool size. Defaults to 10.                                                                                   |
| OPSML_STORAGE_URI          | The location of storage to use. Supports a local file system, AWS, and GCS. Example: `gs://some-bucket`                         |
| OPSML_TRACKING_URI         | Used when logging artifacts to an opsml server (a.k.a., the server which "tracks" artifacts)                                    |
| OPSML_USERNAME             | An optional server username. If the server is setup with login enabled, all clients must use HTTP basic auth with this username |
| OPSML_PASSWORD             | An optional server password. If the server is setup with login enabled, all clients must use HTTP basic auth with this password |
| OPSML_RUN_ID               | If set, the run will be automatically loaded when creating new cards.                                                           |


# Supported Libraries

`Opsml` is designed to work with a variety of ML and data libraries. The following libraries are currently supported:

## Data Libraries

| Name          |  Opsml Implementation    |                                
|---------------|:-----------------------: |
| Pandas        | `PandasData`             |
| Polars        | `PolarsData`             |                                                            
| Torch         | `TorchData`              |                                                                     
| Arrow         | `ArrowData`              |                                                                              
| Numpy         | `NumpyData`              |                        
| Sql           | `SqlData`                |                     
| Text          | `TextDataset`            | 
| Image         | `ImageDataset`           | 

## Model Libraries

| Name          |  Opsml Implementation      |    Example                                          |                                
|-----------------|:-----------------------: |:--------------------------------------------------: |
| Sklearn         | `SklearnModel`           | [link](examples/sklearn/basic.py)                   |
| LightGBM        | `LightGBMModel`          | [link](examples/boosters/lightgbm_boost.py)         |                                                           
| XGBoost         | `XGBoostModel`           | [link](examples/boosters/xgboost_sklearn.py)        |                                                                     
| CatBoost        | `CatBoostModel`          | [link](examples/boosters/catboost_example.py)       |                                                                              
| Torch           | `TorchModel`             | [link](examples/torch/torch_example.py)             |                        
| Torch Lightning | `LightningModel`         | [link](examples/torch/torch_lightning_example.py)   |                     
| TensorFlow      | `TensorFlowModel`        | [link](examples/tensorflow/tf_example.py)           | 
| HuggingFace     | `HuggingFaceModel`       | [link](examples/huggingface/hf_example.py)          | 
| Vowpal Wabbit   | `VowpalWabbitModel`      | [link](examples/vowpal/vowpal_example.py)           | 

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) for creating a great foundation to build from!

<a href="https://github.com/shipt/opsml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shipt/opsml" />
</a>



