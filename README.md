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

<p align="center">
  <a href="#what-is-it">What is it?</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a>  •
  <a href="#advanced-installation-scenarios">Advanced Installation Scenarios</a> •
  <a href="#contributing">Contributing</a>
</p>

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

- **AWS with mysql**: Installs postgres and s3fs dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[s3,mysql]"
  ```

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) and people for creating a great foundation to build from!

<a href="https://github.com/shipt/opsml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shipt/opsml" />
</a>





