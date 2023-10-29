<h1 align="center">
  <br>
  <img src="https://github.com/shipt/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h2 align="center">Tooling for machine learning workflows</h2>

<h1 align="center"><a href="https://thorrester.github.io/opsml-ghpages/">OpsML Documentation</h1>

[![Tests](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml/badge.svg?branch=main)](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)


<h4 align="left">Supported Model Types</h4

[![Keras](https://img.shields.io/badge/Keras-FF0000?logo=keras&logoColor=white)]()
[![Pytorch](https://img.shields.io/badge/PyTorch--EE4C2C.svg?style=flat&logo=pytorch)]()
[![Sklearn](https://img.shields.io/badge/scikit_learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/stable/)
[![Xgboost](https://img.shields.io/badge/Package-XGBoost-blueviolet)](https://xgboost.readthedocs.io/en/stable/)
[![Lightgbm](https://img.shields.io/badge/Package-LightGBM-success)](https://lightgbm.readthedocs.io/en/v3.3.2/)

<h4 align="left">Supported Storage Types</h4>

[![GCS](https://img.shields.io/badge/google_cloud_storage-grey.svg?logo=google-cloud)](https://cloud.google.com/storage)
[![S3](https://img.shields.io/badge/aws_s3-grey?logo=amazons3)](https://aws.amazon.com/)

## Table of Contents
- [What is it?](#what-is-it)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [advanced-installation-scenarios](#advanced-installation-scenarios)
- [Quickstart](#quickstart)
- [Contributing](#contributing)

## What is it?
`OpsML` is a library which simplifies the machine learning project lifecycle.

## Features:
  - **Simple Design**: Standardized design that can easily be incorporated into existing workflows.

  - **Cards**: Track, version, and store a variety of ML artifacts via cards (data, models, runs, pipelines) and a SQL-based card registry system. Think "trading cards for machine learning".

  - **Automation**: Automated processes including Onnx model conversion, api generation from Onnx model, data schema inference, code conversion and packaging for production.

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

- **Server**: Installs necessary packages for setting up an `Fastapi`/`Mlflow` based `Opsml` server
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

## QuickStart

```console
opsml-cli launch-uvicorn-app
```

Open new terminal

```console
export OPSML_TRACKING_URI=http://0.0.0.0:8888
```

Run the following py script

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



## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) and people for creating a great foundation to build from!

<a href="https://github.com/shipt/opsml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shipt/opsml" />
</a>





