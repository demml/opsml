# Installation

Before installing, you'll need to set up your Artifactory credentials.

**Request credentials for Artifactory in Slack `#ask-info-sec`**

Once you have your credentials, set the following variables.
```bash
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_USERNAME=your_username
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_PASSWORD=your_password
```

If using poetry, you must also add the following in your `pyproject.toml`
```toml
[[tool.poetry.source]]
name = "shipt-resolve"
url = "https://artifactory.gcp.shipttech.com/artifactory/api/pypi/pypi-virtual/simple"
default = true
```

Next, add opsml to your environment
```bash
poetry add opsml
```
## Optional Dependencies
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

- **Mlflow**: Installs Mlflow for client-side interaction with an `Opsml` server
  ```bash
  poetry add "opsml[mlflow]"
  ```

- **GCP-mysql**: Installs mysql and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_mysql]"
  ```

- **GCP-postgres**: Installs postgres and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_postgres]"
  ```

### Example setup for gcp-backed postgres with opsml mlflow server

```bash
  poetry add "opsml[gcp_postgres, server, mlflow]"
```

## Environment Variables
`Opsml` requires 1 or 2 environment variables depending on if you are using it as an all-in-one interface (no proxy) or you are using it as an interface to interact with an `Opsml` [server](server/overview.md).
 
- **OPSML_TRACKING_URI**: This is the sql tracking uri to your card registry database. If interacting with an `Opsml` server, this will be the http address of the server. If this variable is not set, it will default to a local `SQLite` connection.

- **OPSML_STORAGE_URI**: This is the storage uri to use for storing ml artifacts (models, data, figures, etc.). `Opsml` currently supports local file systems and google cloud storage.
If running `Opsml` as an all-in-one interface, this variable is required and will default to a local folder if not specified. If interacting with an `Opsml` server, this variable does not need to be set.