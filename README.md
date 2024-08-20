<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h2 align="center">OSS Version 3.0.0 Coming Soon!</h2>


<h2 align="center">Universal Machine Learning Artifact Registration Platform</h2>

<h1 align="center"><a href="https://demml.github.io/opsml/">OpsML Documentation</h1>

[![Unit Tests](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml)
[![Examples](https://github.com/demml/opsml/actions/workflows/examples.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/examples.yml)
[![Storage Integration Tests](https://github.com/demml/opsml/actions/workflows/integration.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/integration.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![AWS S3](https://img.shields.io/badge/AWS%20S3-orange)](https://aws.amazon.com/s3/)
[![Google Cloud Storage](https://img.shields.io/badge/GCS-success)](https://cloud.google.com/storage)
[![Azure](https://img.shields.io/badge/Azure-%230072C6)](https://azure.microsoft.com/en-us/products/storage/blobs)

## **What is it?**

`OpsML` is a comprehensive toolkit designed to streamline and standardize machine learning operations. It offers:

- Universal Registration System: A centralized platform for managing all ML artifacts.
- Standardized Governance: Implement consistent practices across data science and engineering teams.
- Artifact Lifecycle Management: Robust tracking, versioning, and storage solutions for all ML components.
- Reproducible Workflows: Establish repeatable patterns for ML project management.
- Cross-functional Compatibility: Bridge the gap between data science experimentation and production engineering.
- Version Control for ML: Apply software engineering best practices to machine learning artifacts.
- Metadata-Driven Approach: Enhance discoverability and traceability of models, datasets, and experiments.

This toolkit empowers teams to maintain rigorous control over their ML projects, from initial data preprocessing to model deployment and monitoring, all within a unified, scalable framework.


## **Why OpsML?**

OpsML addresses a critical gap in the ML ecosystem: the lack of a universal standard for artifact registration and governance. Our experience with various open-source and proprietary tools revealed a persistent need to integrate disparate systems for effective artifact management and deployment. This led to the development of OpsML, a unified framework designed to streamline ML operations.
Key Features:

- **Modular Architecture**: Seamlessly integrates into existing ML pipelines and workflows.
- **Card-based Artifact System**: Implements a SQL-based registry for tracking, versioning, and storing ML artifacts (data, models, runs, projects). Think of it as `trading cards for machine learning`.
- **Strong Type Enforcement**: Ensures data integrity with built-in type checking for data and model artifacts.
- **Extensive Library Support**: Compatible with a wide range of ML and data processing libraries.
- **Automated ML Ops**:
    - Auto-conversion to ONNX format
    - Intelligent metadata generation
    - Streamlined production packaging
    - Out of the box model monitoring<sup>*</sup>
- **Unified Governance Model**: Provides a consistent framework for managing the entire ML lifecycle, from experimentation to production.
- **Scalable Design**: Accommodates growing complexity of ML projects and increasing team sizes.

OpsML aims to be the common language for ML artifact management, reducing cognitive overhead and enabling teams to focus on model development and deployment rather than operational complexities.

<sup>
* OpsML is integrated with `Scouter` out of the box. However, a `Scouter` server instance is required to use this feature.
</sup>

## Incorporate into Existing Workflows

Add quality control to your ML projects with little effort! With `OpsML`, data and models are added to interfaces and cards, which are then registered via card registries. 

# Incorporate into Existing Workflows

Given its simple and modular design, `OpsML` can be easily incorporated into existing workflows. 

<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-chip.png?raw=true"  width="800" alt="opsml logo"/>
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

By default, `OpsML` will log artifacts and experiments locally. To change this behavior and log to a remote server, you'll need to set the following environment variables:

```shell
export OPSML_TRACKING_URI=${YOUR_TRACKING_URI}
```

You can find more information on how to set up the tracking and storage uris [here](https://demml.github.io/opsml/installation/).

## Quickstart

If running the example below locally, with a local server, make sure to install the `server` extra:

```bash 
poetry add "opsml[server]"
```

```python
from sklearn.linear_model import LinearRegression
from opsml import CardInfo, CardRegistries, DataCard, ModelCard, PandasData, SklearnModel
from opsml.helpers.data import create_fake_data

# Setup
info = CardInfo(name="linear-regression", repository="opsml", contact="user@email.com")
registries = CardRegistries()

# Create and register DataCard
X, y = create_fake_data(n_samples=1000, task_type="regression")
X["target"] = y

data_interface = PandasData(
    data=X,
    data_splits=[
        DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
        DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
    ],
    dependent_vars=["target"]
)

datacard = DataCard(interface=data_interface, info=info)
registries.data.register_card(card=datacard)

# Train model
data = datacard.split_data()
reg = LinearRegression().fit(data["train"].X, data["train"].y)

# Create and register ModelCard
model_interface = SklearnModel(
    model=reg,
    sample_data=data["train"].X,
    task_type="regression"
)

modelcard = ModelCard(
    interface=model_interface,
    info=info,
    to_onnx=True,
    datacard_uid=datacard.uid
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
- [Supported Libraries](#supported-libraries)
  - [Data Libraries](#data-libraries)
  - [Model Libraries](#model-libraries)
  - [Contributing](#contributing)

## Usage

Now that `OpsML` is installed, you're ready to start using it!

It's time to point you to the official [Documentation Website](https://demml.github.io/opsml/) for more information on how to use `OpsML`

## Advanced Installation Scenarios

see [Installation](https://demml.github.io/opsml/installation/) for more information on how to install `OpsML` in different environments.


# Supported Libraries

`OpsML` is designed to work with a variety of ML and data libraries. The following libraries are currently supported:

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