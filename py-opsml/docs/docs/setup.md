
## Choose your adventure

The recommended way to use OpsML is to run the server separately and connect to it from your client. This allows you to take advantage of the full power of OpsML and its features. 

[Client Mode](#client-mode){ .md-button .md-button--primary } [Server Mode](#server-mode){ .md-button .md-button--primary }

## Client Mode

If you are connecting to an OpsML server that is already setup and running, all you need to do is set the `OPSML_TRACKING_URI` and you're good to go. 

```console
$ export OPSML_TRACKING_URI={your_server_uri}
```
## Server Mode

Depending on your use case there are a few different ways to setup and run the server.

### Docker

The recommended way to run the server is to use Docker. With every release of OpsML, we build and publish new Docker images that you can use to run the server. You can find the latest images on [Docker Hub](https://hub.docker.com/r/demml/opsml). 

In most cases, you can run the server with the following command; however, you may wish to use our docker images as base images to build your own custom images.

```console
$ docker run -p 3000:3000 demml/opsml
```

### Binary

In addition to docker images, we also build and publish new binaries with every release of OpsML. These can be download via github and executed directly. 


### Development

As mentioned in the installation section, you can also start the server via the CLI; however, this is not recommended for production use cases as it requires a python runtime to be installed.. The *Docker* and *Binary* methods do not require a python runtime to be installed as they are 100% Rust implementations.

!!! Note

    While the OpsML CLI is written in Rust, it is exposed via PyO3 and requires a python runtime to be installed. This is not the case for the server, which is a pure Rust implementation with no python bindings.

```console
$ opsml start ui
```

### Running the Server

OpsML support multiple backends for both the database and storage. By default, OpsML will use SQLite for the database and local file storage for the storage backend. You can change this by setting the `OPSML_TRACKING_URI` and `OPSML_STORAGE_URI` environment variables. 

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


### Environment Variables

Apart from the `OPSML_TRACKING_URI` and `OPSML_STORAGE_URI` environment variables, there are a few other environment variables that you can set to configure the server to your liking.

#### OpsML Server Environment Variables

- `APP_ENV`: The current environment. This can be set to `development`, `staging` or `production` or anything else you'd want. The default is `development`.
- `OPSML_SERVER_PORT`: The port that the server will run on. The default is `3000`.
- `OPSML_ENCRYPT_KEY`: The master encryption key used to encrypt the data at rest. If not set, OpsML will use a default **deterministic** key. This is not recommended for production use cases. OpsML requires a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key using the following command with the OpsML CLI:
  
```console
$ opsml generate key --password {your_password}
```

    The encryption key (aka jwt_key) is one of the most important pieces to OpsML's security system. It is used to derive new keys for each artifact, which in-turn are used to encrypt data, and is used generate short-lived JWT tokens for authentication.

- `OPSML_REFRESH_SECRET`: The secret used to sign the refresh tokens. This is used to verify the integrity of the refresh tokens. If not set, OpsML will use a default **deterministic** key. This is not recommended for production use cases. OpsML requires a pbdkdf2::HmacSha256 key with a length of 32 bytes. You can generate a key similar to the `OPSML_ENCRYPT_KEY` key.
  
#### Scouter Environment Variables

If you are configuring OpsML to user Scouter for model monitoring, you will need to set the following environment variables as well:

- `SCOUTER_SERVER_URI`: The host of the Scouter server.
- `SCOUTER_BOOTSTRAP_TOKEN`: The bootstrap token used to authenticate with the Scouter server and exchange refresh tokens. This is used to verify the integrity of the Scouter tokens. If not set, OpsML will use a default **deterministic** key.
