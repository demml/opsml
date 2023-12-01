# Installation

### Poetry

```bash
poetry add opsml
```

### Pip

```bash
pip install opsml
```

## Optional Dependencies
`Opsml` is designed to work with a variety of 3rd-party integrations depending on your use-case.

Types of extras that can be installed:

- **Postgres**: Installs postgres pyscopg2 dependency to be used with `Opsml`
  ```bash
  poetry add "opsml[postgres]"
  ```

- **Server**: Installs necessary packages for setting up a `Fastapi` based `Opsml` server
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

### Example setup for gcs storage and postgres with opsml server

```bash
  poetry add "opsml[gcs, postgres, server]"
```

## Environment Variables
`Opsml` requires 1 or 2 environment variables depending on if you are using it as an all-in-one interface (no proxy) or you are using it as an interface to interact with an `Opsml` [server](server/overview.md).

- **OPSML_TRACKING_URI**: This is the sql tracking uri to your card registry database. If interacting with an `Opsml` server, this will be the http address of the server. If this variable is not set, it will default to a local `SQLite` connection.

- **OPSML_STORAGE_URI**: This is the storage uri to use for storing ml artifacts (models, data, figures, etc.). `Opsml` currently supports local file systems and google cloud storage.
If running `Opsml` as an all-in-one interface, this variable is required and will default to a local folder if not specified. If interacting with an `Opsml` server, this variable does not need to be set.

## TLDR Scenarios

**Server is already setup and I need to interact with it from the client side (notebook, python script, cli, etc.)**:

  - Set `OPSML_TRACKING_URI` to the http address of the server

**I need to setup the Server**:

  - Set `OPSML_TRACKING_URI` to the sql tracking uri of your card registry database
  - Set `OPSML_STORAGE_URI` to the storage uri of your choice
  - Follow instructions in [server](server/overview.md) docs