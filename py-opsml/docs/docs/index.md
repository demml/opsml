<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h3 align="center">Quality Control for the Machine Learning Artifacts</h3>
---

[![Unit Tests](https://github.com/demml/opsml/actions/workflows/lints-test.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lints-test.yml)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

## **What is it?**

`OpsML` is a developer-first ML operations platform focused on injecting quality control into machine learning artifact management. `OpsML` provides a unified and ergonomic interface and experience for managing ML artifacts, enabling teams to collaborate more effectively and deploy with confidence, all while reducing engineering overhead and providing piece of mind.

## See it in action
```python {upgrade="skip" title="Quickstart" requires=">=3.10"}
from opsml.helpers.data import create_fake_data
from typing import Tuple, cast
import pandas as pd
from opsml import SklearnModel, CardRegistry, TaskType,  ModelCard
from sklearn import ensemble  # type: ignore

# start registries
reg = CardRegistry(RegistryType.Model)

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

# Create and train model
classifier = ensemble.RandomForestClassifier(n_estimators=5)
classifier.fit(X.to_numpy(), y.to_numpy().ravel())

model_interface = SklearnModel(
    model=classifier,
    sample_data=X,
    task_type=TaskType.Classification,
)

modelcard = ModelCard(
    interface=model_interface,
    space="opsml",
    name="my_model",
    to_onnx=True,  # aut-convert to onnx (optional)
)

# register model
reg.model.register_card(modelcard)

# This code will run as is
```

## **What is Quality Control?**

Quality control in the context of `OpsML` refers to:

### Developer-First Experience
- **Zero-friction Integration** - Drop into existing ML workflows in minutes
- **Type-safe and efficient by Design** - Rust in the back, python in the front<sup>*</sup>. Catch errors before they hit production
- **Unified API** - One consistent interface for all ML frameworks
- **Environment Parity** - Same experience from development to production
- **Dependency Overhead** - One dependency for all ML artifact management

### Built to Scale
- **Trading Cards for ML** - Manage ML artifacts like trading cards - collect, organize, share
- **Cloud-Ready** - Native support for AWS, GCP, Azure
- **Database Agnostic** - Support for SQLite, MySQL, Postgres
- **Modular Design** - Use what you need, leave what you don't

### Production Ready
- **High-Performance Server** - Built in Rust for speed, reliability and concurrency
- **Built-in Security** - Authentication and encryption out of the box
- **Audit-Ready** - Complete artifact lineage and versioning
- **Standardized Governance Workflows** - Consistent patterns to use across teams
- **Built-in Monitoring** - Integrated with Scouter

<sup>
*OpsML is written in Rust and is exposed via a Python API built with PyO3.
</sup>
