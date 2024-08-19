<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h4 align="center">A Universal Artifact Registration System for Machine Learning</h4>
---

[![Unit Tests](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml)
[![Examples](https://github.com/demml/opsml/actions/workflows/examples.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/examples.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)

## **What is it?**

`OpsML` provides tooling that enables data science and engineering teams to better govern and manage their machine learning projects and artifacts by providing a standardized and universal registration system and repeatable patterns for tracking, versioning and storing ML artifacts.


## **Why?**

The core focus of `OpsML` is artifact registration, management and governance. After using various open-source and vendor tooling to manage different aspects of the machine learning project lifecycle, we found that we were still spending ample time gluing different tooling together in order to adequately govern, manage and deploy artifacts. Moreover, <b>machine learning currently lacks a universal standard for artifact registration and governance<b>, which makes managing machine learning projects and systems challenging. And given how expansive the machine learning tooling ecosystem is, and how each tool tends to have it's own way of saving, storing and tracking artifacts, we decided to build `OpsML` with the goal of providing a common framework.


## **Features**:
  - **Simple Design**: Standardized design that can easily be incorporated into existing projects.

  - **Cards**: Track, version and store a variety of ML artifacts via cards (data, models, runs, projects) and a SQL-based card registry system. Think `trading cards for machine learning`.

  - **Type Checking**: Strongly typed and type checking for data and model artifacts.

  - **Support**: Robust support for a variety of ML and data libraries.

  - **Automation**: Automated processes including onnx model conversion, metadata creation and production packaging.

## Incorporate into Existing Workflows

Add quality control to your ML projects with little effort! With `opsml`, data and models are represented as `cards` and stored in a `card registry`. This allows for easy versioning, tracking and storage of ML artifacts. 

<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-chip.png?raw=true"  width="900" alt="opsml logo"/>
  <br>
</h1>

## Our Goal

Our goal is 2-fold. (1) We want to provide a simple and consistent interface for managing and tracking ML artifacts that is easy for DSs to use and incorporate, and (2) we want to inject quality control by providing standardized interfaces to DSs that automate the creation and governance of ML artifacts for our engineers.


## Why Use OpsML vs other open source or vendor tooling?

With the plethora of available ML tooling it can be difficult to decide which tooling to use. The following are some reasons why you might want to use `Opsml` and why we created it.

- Need for a consistent and standardized ML workflow to use in your organization
- You want to use a tool that is open source and continually developed
- You want all artifacts to be given the same priority (no more treating data as less of a priority than models)
- Don't want to worry about implementation details (how to version, store and track artifacts)
- You'd like to have auto-generated metadata that meets engineering standards and can be used in production
- You want to be able to share artifacts and workflows across teams

### Key Features

| Feature | OpsML | Others |
|---------|:-------:|:--------:|
| **Built in Model and Data Type Checking** | ✅ | ❌ |
| **Stream Artifacts by Default** | ✅ | ❌ |
| **End to End Observability** | ✅ | ❌ |
| **No Shared Environments (no cross-polluting staging and prod)** | ✅ | ❌ |
| **Auto-Onnx Conversion** | ✅ | ❌ |
| **Auditability or Model and Data Assets** | ✅ | ❌ |
| **Out of the Box Model Monitoring and Data Profiling** | ✅ | ❌ |
| **Automated Metadata Generation** | ✅ | ❌ (for most) |
| **Artifact Tracking** - Data, Models, Runs | ✅ | ❌ (for most) |
| **Artifact Semantic Versioning** | ✅ | ❌ (for most) |
| **Support for Multiple Cloud Providers** | ✅ | ✅ |
| **Support for Multiple Databases** | ✅ | ✅ |
| **Codebase is Readable** | ✅ | 🙏 |

To get started using `OpsML`, check out the [installation](installation.md) and [quickstart](quickstart.md) guides.

# Supported Libraries

`Opsml` is designed to work with a variety of ML and data libraries. The following libraries are currently supported out of the box. OpsML also supports custom data and model interfaces, so if you're library isn't supported, you can create your own interface as well as request that we add it to the library 😃


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
| Sklearn         | `SklearnModel`           | [link](https://github.com/demml/opsml/blob/main/examples/sklearn/basic.py)                   |
| LightGBM        | `LightGBMModel`          | [link](https://github.com/demml/opsml/blob/main/examples/boosters/lightgbm_boost.py)         |                                             
| XGBoost         | `XGBoostModel`           | [link](https://github.com/demml/opsml/blob/main/examples/boosters/xgboost_sklearn.py)        |                                                       
| CatBoost        | `CatBoostModel`          | [link](https://github.com/demml/opsml/blob/main/examples/boosters/catboost_example.py)       |                                                                
| Torch           | `TorchModel`             | [link](https://github.com/demml/opsml/blob/main/examples/torch/torch_example.py)             |                        
| Torch Lightning | `LightningModel`         | [link](https://github.com/demml/opsml/blob/main/examples/torch/torch_lightning_example.py)   |                     
| TensorFlow      | `TensorFlowModel`        | [link](https://github.com/demml/opsml/blob/main/examples/tensorflow/tf_example.py)          | 
| HuggingFace     | `HuggingFaceModel`       | [link](https://github.com/demml/opsml/blob/main/examples/huggingface/hf_example.py)         |
| VowpalWabbit    | `VowpalWabbitModel``     | [link](https://github.com/demml/opsml/blob/main/examples/vowpal/vowpal_example.py)          |

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](https://github.com/demml/opsml/blob/main/CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](https://github.com/demml/opsml/blob/main/ATTRIBUTIONS.md) and people for creating a great foundation to build from!

<a href="https://github.com/demml/opsml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=demml/opsml" />
</a>


