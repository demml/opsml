# `Opsml` Server Setup

In addition to using `Opsml` as a stand-alone python package, it can also be used as a server (`FastApi`) providing a proxy interface between data scientists and backend infrastructure (**recommended approach**). What this means for **data scientists**, is that they can use `Opsml` as they normally would without having to set any credentials apart from the http proxy uri. For **engineers**, this means that they can control the infrastucture, databases, and overall server setup based on their specifications and security requirements. More on this can be found [here](../engineering/ownership.md)


## Registry Architecture
![](opsml-registry-arch.png){ align=center }


## Project Run Flow Architecture
![](server-proxy-arch.png){ align=center }

---

## **Setup**
You can setup the `Opsml` server based on your repository needs. For our purposes at `Shipt`, we tend to follow a conventional setup whereby we host Docker images via K8s. For this setup up, we typically will install `Opsml` and its dependencies into a Dockerfile.

### Required Env Vars

As mentioned [here](../installation.md) `Opsml` expects 2 variables to be set (these can be set in an Dockerfile or at webserver runtime).

#### OPSML_TRACKING_URI

This is the tracking uri of your backend database.

Example:

`OPSML_TRACKING_URI=postgresql://user:pass@host:port/database_name`

#### OPSML_STORAGE_URI

This is the storage uri of your storage backend (e.g. GCP, AWS).

Example:

`OPSML_STORAGE_URI=gs://my-google-cloud-bucket`

#### OPSML_POOL_SIZE (optional)

Default pool size to use with sqlalchemy engine. If not set, will default to 10.

Example:

`OPSML_POOL_SIZE=10`

#### OPSML_MAX_OVERFLOW (optional)

Default max overflow to use with sqlalchemy engine. If not set, will default to 5.

Example:

`OPSML_MAX_OVERFLOW=10`

### Run Command

- During local development/testing, you can spin up and test the `Opsml` server via the **CLI** command `opsml-uvicorn-server` which will launch a Uvicorn server.
- For production, it is recommended that you run Gunicorn.
- The following command can be used to run a Gunicorn `Opsml` server.

`gunicorn -k uvicorn.workers.UvicornWorker --config=./app/gunicorn_conf.py --bind=0.0.0.0:3000 "opsml.app.main:run_app(login=False)"`

### Example pyproject.toml for an Opsml Server

```
[tool.poetry]
name = "opsml-server"
version = "0.1.0"
description = ""
authors = ["ml-platform"]

[tool.poetry.dependencies]
python = ">=3.9,<=3.11"
opsml = {version = "^2.0.0", extras = ["gcs", "postgres", "server"]}
```