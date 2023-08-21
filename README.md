<h1 align="center">
  <br>
  <img src="images/opsml-logo.png"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h2 align="center">Tooling for machine learning workflows</h2>

<h1 align="center"><a href="https://didactic-bassoon-l5emw7m.pages.github.io/">OpsML Documentation</h1>

<p align="center">

  <a href="https://www.python.org/downloads/release/python-390/">
  <img alt="Python" src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Blue_Python_3.9_Shield_Badge.svg" />

  <img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg" />

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

It's time to point you to the official [Documentation Website](https://didactic-bassoon-l5emw7m.pages.github.io/) for more information on how to use `opsml`


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

- **GCP-mysql**: Installs mysql and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_mysql]"
  ```

- **GCP-postgres**: Installs postgres and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_postgres]"
  ```

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) for creating a great foundation to build from!
