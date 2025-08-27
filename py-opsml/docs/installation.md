# Installation

Install OpsML with your preferred package manager. OpsML is built and distributed through PyPi and comes in 2 flavors: **client** and **server**.

## Server and client installation

If you want to work in a development environment and don't want to setup an independent server (we recommend that you do!), you can install both the client and server components with the following command:

=== "uv"

    ```console
    $ uv add opsml
    ```

=== "pip"

    ```console
    $ pip install opsml
    ```

## Client installation

If you already have a server up and running, as you would in an enterprise environment, you can install the client components with the following command:

=== "uv"

    ```console
    $ uv add opsml-client
    ```

=== "pip"

    ```console
    $ pip install opsml-client
    ```

## Basic Usage

OpsML is designed for both development and production use cases, meaning you can run it in either server mode or client mode. 

- **Server mode**: You are directly connecting to both the database and storage backends. 
- **Client mode**: You are connecting to an OpsML server that is already running and managing the database and storage backends for you. 

While it's recommended to setup the server separately for production and enterprise use cases, we understand sometimes you just want to get up and running quickly to test things out or work locally.

???tip "Server Mode"
    The OpsML server is written in 100% Rust using the [Axum](https://github.com/tokio-rs/axum/) framework. On every release of OpsML, we build, tag and publish new docker images that you can use to run the server. You can also build the server from source or download the pre-built binary from our release artifacts.
   

## Run Before Walking

Let's make sure everything is setup correctly before moving on to other sections. The following demo will populate a few Cards into a database that you can then visualize in the UI. You will also need to make sure you install sklearn and pandas if you haven't already. You can do this with the following command:

```bash
pip install pandas scikit-learn
```

???warning Note
    This is intended for demo purposes only. When you you are ready to use OpsML in a production environment, take a look at the [Server Setup](./docs/setup/overview.md) section to learn how to setup the server and connect to it from your client.
   

Run the following CLI commands from within your python environment to make sure everything is working as expected.

**Note**: This will create a new SQLite database in the current directory.

This command will create a local cache, pull the latest version of the UI from the OpsML repository and run the server. The server is written entirely in Rust and is exposed as a SvelteKit SPA and does not come prepackaged with OpsML.

```bash
opsml ui start
```

This will create a new SQLite database in the current directory and populate it with a few Cards. You can then visualize the Cards in the UI by running the following command:

```bash
opsml demo
```

