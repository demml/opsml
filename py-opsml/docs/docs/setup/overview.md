
## Choose your adventure

The recommended way to use opsml is to run the server separately and connect to it from your client. This allows you to take advantage of the full power of Opsml and its features.

[Client Mode](#client-mode){ .md-button .md-button--primary } [Server Mode](#server-mode){ .md-button .md-button--primary }

## Client Mode

If you are connecting to an Opsml server that is already setup and running, all you need to do is set the `OPSML_TRACKING_URI` and you're good to go.

```console
$ export OPSML_TRACKING_URI={your_server_uri}
```

You can also set the following optional environment variables if your server has authenitcation enabled:
```console
$ export OPSML_USERNAME={your_username}
$ export OPSML_PASSWORD={your_password}
```

## Server Mode

Depending on your use case there are a few different ways to setup and run the server.

### Docker

The recommended way to run the server is to use Docker or any other container service. With every release of opsml, we build and publish new container images that you can use to run the server and UI. You can find the latest images on [Docker Hub](https://hub.docker.com/r/demml/opsml).

In most cases, you can run the server with the following command; however, you may wish to use our docker images as base images to build your own custom images.

```console
$ docker run -p 8080:8000 demml/opsml:ubuntu-armd64-{version}
```

### What's in the container?

The server container image is home to both the UI ([sveltekit nodejs app](https://svelte.dev/docs/kit/introduction)) and the opsml server backend ([Axum](https://github.com/tokio-rs/axum)). The UI is always exposed on port `3000` and the server port is exposed on `8080`. NGINX is used as a reverse proxy to route requests to the appropriate service (see `docker/extras` folder for the NGINX configuration) and exposes everything on port `8000` (configurable through `OPSML_SERVER_PORT`).

**Note:** The container images are run through an entrypoint script that starts the UI, server, and NGINX services and ensures that they are all running properly. See `docker/official/extras/entrypoint.sh` for more details. The entrypoint does not make use of any process managers like `supervisord` or `systemd` as we prefer the container orchestration system (e.g., Kubernetes etc.) to handle process management.

### Binary

In addition to docker images, we also build and publish new binaries with every release of opsml. These can be download via github and executed directly.

### Development

As mentioned in the installation section, you can also start the server via the CLI; however, this is not recommended for production use cases as it requires a python runtime to be installed. We recommend using the prebuilt containers for production use cases as they only require node (pre-installed in the container) to run the UI and the opsml server binary.

!!! Note

    While the opsml CLI is written in Rust, it is exposed via PyO3 and requires a python runtime to be installed. Node will also be required to run the UI locally.

```console
$ opsml start ui
```

### Running the Server

opsml supports multiple backends for both the database and storage client. By default, opsml will use SQLite for the database and local file storage for the storage backend. You can change this by setting the `OPSML_TRACKING_URI` and `OPSML_STORAGE_URI` environment variables, respectively.

To run the server with a different database backend, you can set the `OPSML_TRACKING_URI` environment variable to the desired backend. For example, to use Postgres, you can set the following environment variable:

```console
$ export OPSML_TRACKING_URI=postgresql://user:password@localhost:5432/opsml
```

Supported Database backends:

- SQLite
- Postgres
- MySQL

To run the server with a different storage backend, you can set the `OPSML_STORAGE_URI` environment variable to the desired backend. For example, to use S3, you can set the following environment variable:

```console
$ export OPSML_STORAGE_URI=s3://bucket-name
```

Supported Storage backends:

- Local File Storage
- S3
- GCS
- Azure Blob Storage

!!!info
    Ensure the required storage credentials are set appropriately in your environment

#### Storage Credentials

##### Google Cloud Storage

- `GOOGLE_ACCOUNT_JSON_BASE64`: Environment variables that contains the base64 encoded JSON key for the service account.
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Environment variable that contains the JSON key for the service account.
- `GOOGLE_APPLICATION_CREDENTIALS`: Environment variable that contains the path to the credential file.

##### Amazon S3

- Opsml uses the [aws_sdk_s3](https://docs.rs/aws-sdk-s3/1.82.0/aws_sdk_s3/) and [aws_config](https://docs.rs/aws-config/1.6.1/aws_config/#examples) crates to handle S3 storage. Thus, all credential configurations supported by the rust crate are supported by opsml.

##### Azure Blob Storage

- Opsml uses the [azure-identity](https://docs.rs/azure_identity/latest/azure_identity/) crate to handle authentication.

- In addition to credentials, to use Azure Blob Storage, you will need to set the following environment variable:
    - `AZURE_STORAGE_ACCOUNT`: The name of the storage account.


### Environment Variables

Apart from the `OPSML_TRACKING_URI` and `OPSML_STORAGE_URI` environment variables, there are a few other environment variables that you can set to configure the server to your liking.

#### OpsML Server Environment Variables

- `APP_ENV`: The current environment. This can be set to `development`, `staging` or `production` or anything else you'd want. The default is `development`.
- `OPSML_SERVER_PORT`: The port that the container will run on. The default is `8000`.
- `OPSML_ENCRYPT_KEY`: The master encryption key used to encrypt the data at rest. If not set, opsml will use a default **deterministic** key. This is not recommended for production use cases. opsml requires a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key using the following command with the opsml CLI:

```console
$ opsml generate key --password {your_password}
```

The encryption key (aka jwt_key) is one of the most important pieces to opsml's security system. It is used to derive new keys for each artifact, which in-turn are used to encrypt data, and is used generate short-lived JWT tokens for authentication.

- `OPSML_REFRESH_SECRET`: The secret used to sign the refresh tokens. This is used to verify the integrity of the refresh tokens. If not set, opsml will use a default **deterministic** key. This is not recommended for production use cases. opsml requires a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key similar to the `OPSML_ENCRYPT_KEY` key.
- `OPSML_MAX_POOL_CONNECTIONS`: The maximum number of connections to the database. The default is `10`.
- `LOG_LEVEL`: The log level for the server and UI. This can be set to `error`, `warn`, `info`, `debug` or `trace`. The default is `info`.
- `LOG_JSON`: Whether to log in JSON format or not. This can be set to `true` or `false`. The default is `false`.

#### Scouter Environment Variables

If you are configuring opsml to use Scouter for model monitoring, you will need to set the following environment variables as well:

- `SCOUTER_SERVER_URI`: The host of the Scouter server.
- `SCOUTER_AUTH_TOKEN`: The secret token used to authenticate with the Scouter server and exchange refresh tokens. This is used to verify the integrity of the Scouter tokens. If not set, opsml will use a default **deterministic** key. In keeping with the other opsml secret keys, the `SCOUTER_AUTH_TOKEN` is a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key similar to the `OPSML_ENCRYPT_KEY` key if you haven't already done so.
- `SCOUTER_BOOTSTRAP_TOKEN`: The bootstrap token is used to sync users across both OpsML and Scouter. This is also a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key similar to the `OPSML_ENCRYPT_KEY` key if you haven't already done so.
