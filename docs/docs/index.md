<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h4 align="center">A Universal Artifact Registration System for Machine Learning</h4>
---

[![Unit Tests](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lint-unit-tests.yml)
[![Examples](https://github.com/demml/opsml/actions/workflows/examples.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/examples.yml)
[![Storage Integration Tests](https://github.com/demml/opsml/actions/workflows/integration.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/integration.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![AWS S3](https://img.shields.io/badge/AWS%20S3-orange)](https://aws.amazon.com/s3/)
[![Google Cloud Storage](https://img.shields.io/badge/GCS-success)](https://cloud.google.com/storage)
[![Azure](https://img.shields.io/badge/Azure-%230072C6)](https://azure.microsoft.com/en-us/products/storage/blobs)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

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

Add quality control to your ML projects with little effort! With `OpsML`, data and models are represented as `cards` and stored in a `card registry`. This allows for easy versioning, tracking and storage of ML artifacts. 

<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-chip.png?raw=true"  width="900" alt="opsml logo"/>
  <br>
</h1>

## Our Mission

Our mission with OpsML is twofold:

1. **Streamlined Artifact Management**
     - Provide a intuitive, consistent API for ML artifact tracking and management
     - Design a low-friction interface that data scientists can easily adopt and integrate into their workflows
     - Minimize the learning curve for adopting robust ML ops practices

2. **Automated Quality Assurance**
      - Implement standardized interfaces that enforce best practices in ML artifact creation and governance
      - Automate critical aspects of artifact management to reduce human error and inconsistency
      - Bridge the gap between data science experimentation and production engineering requirements
      - Facilitate seamless handoffs between data science and engineering teams

## Why Use OpsML vs other open source or vendor tooling?

Navigating the crowded landscape of ML tools can be challenging. Here's why Opsml stands out and why we developed it:

1. Standardized ML Workflows: Implement a consistent, reproducible workflow across your organization.
2. Open-Source Advantage: Benefit from continuous development and community-driven improvements.
3. Artifact Equality: Elevate data to the same priority as models in your ML lifecycle.
4. Abstraction of Implementation Details: Focus on your core ML tasks while Opsml handles versioning, storage, and tracking of artifacts.
5. Production-Ready Metadata: Automatically generate metadata that meets stringent engineering standards and is deployment-ready.
6. Cross-Team Collaboration: Easily share artifacts and workflows, fostering synergy between data science and engineering teams.
7. Reduced Technical Debt: Streamline your ML operations with a tool designed for long-term maintainability and scalability.

### Key Features

| Feature | OpsML | Others |
|---------|:-------:|:--------:|
| **Built-in Type Checking for Models & Data** | ✅ | ❌ |
| **Default Artifact Streaming** | ✅ | ❌ |
| **Full-Stack Observability** | ✅ | ❌ |
| **Isolated Environments (No Staging/Prod Conflicts)** | ✅ | ❌ |
| **Automated ONNX Conversion** | ✅ | ❌ |
| **Comprehensive Model & Data Asset Auditing** | ✅ | ❌ |
| **Out-of-the-Box Model Monitoring & Data Profiling** | ✅ | ❌ |
| **Automated Metadata Generation** | ✅ | ❌ (rare) |
| **Granular Artifact Tracking (Data, Models, Runs)** - Data, Models, Runs | ✅ | ❌ (uncommon) |
| **SemVer for All Artifacts** | ✅ | ❌ (rare) |
| **Multi-Cloud Compatibility** | ✅ | ✅ |
| **Multi-Database Support** | ✅ | ✅ |
| **Clean, Maintainable Codebase** | ✅ | 🤔 |



To get started using `OpsML`, check out the [installation](installation.md) and [quickstart](quickstart.md) guides.

# Supported Libraries

`OpsML` is designed to work with a variety of ML and data libraries. The following libraries are currently supported out of the box. OpsML also supports custom data and model interfaces, so if you're library isn't supported, you can create your own interface as well as request that we add it to the library 😃


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


