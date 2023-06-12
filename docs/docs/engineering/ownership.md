# Ownership

In many organizations there is often a separation of concerns between data science and engineering when it comes to data science tooling and infrastructure. Thus, with something like `Opsml` it's appropriate to think "who owns what?" or "where does data science and engineering fit into the lifecycle, use, and management of a system like this?". The goal of `Opsml` is to provide an interface into infrastructure that data scientists use and engineering owns/controls. The diagram below is one example of this separation of concerns.

## **Architecture of Opsml Proxy Setup**

<p align="center">
  <img src="../../images/opsml-example-arch.png" width="1419" height="845"/>
</p>

### General Setup

**Note** - This is an example setup to give an overview of the separation between data science and engineering

`Opsml` is packaged and deployed as a proxy system where a server is set up and exposed via a callable api that data scientists set as an environment variable (OPSML_TRACKING_URI). When data scientists use `Opsml` they will interact with the server through a client API that is automatically configured when `Opsml` is loaded in python.

#### Parts Owned by Engineering

- `Opsml` server that is packaged into a docker container and deployed through K8s
- Storage system (local or cloud) that will be used to store `ArtifactCard` artifacts (models, data, figures, etc.) 
- Database that will be use to store `ArtifactCard` metadata. This will typically be a mysql or postgresql database
- K8s and compute infrastructure for hosting applications
- CI/CD build process

#### Other Considerations

- In this scenario it is expected that the infrastructure hosting the `Opsml` server is also responsible for authentication and security. As an example, the host system may be placed on an internal network that is only accessible via authentication through a VPN. `Opsml` was built to be an ML tooling interface, not a security system. Thus, security should be configured on the host system.
- Credentialing for external systems (storage, databases, etc.) should also be configured and embedded in the environment that hosts the `Opsml` server. This enables engineering to limit and control the credentials needed for `Opsml`. It also eliminates the need for data scientists to have to specify credentials when working with `Opsml` (apart for security authentication).

### Scenario 1: DS Workflows

This scenario covers the typical data science workflow and tasks that include exploratory analysis, model training and model evaluation. As part of this workflow, a data scientist will produce various `ArtifactCards` and store their attributes/metadata through client/server communication.

### Scenario 2: Model Deployment

In this scenario, a data scientist or ml engineer creates the custom api logic for their model ([FastApi](https://fastapi.tiangolo.com/) for example) and specifies resources to deploy in a custom configuration or specification file. For this example, assume the engineering team has set up an automated process whereby changes to the configuration file and push/tags trigger a CI/CD process that builds and serves a new model api. Upon build kickoff, the model specified in the configuration file is downloaded from the `Opsml` server and packaged along with the api code into a docker container. This docker container is then deployed on K8s where the api is served and ready for requests.


# Environment

It is recommended to setup `Opsml` on each of your environments (dev/staging and prod). This is slightly different than other DS tooling packages and was done in order to follow best practices is systems/infra design. As a result, you will have separate registries across environments that will *not* be linked. Thus, versions across staging and prod may not be in sync, which is not necessarily an issue considering **prod** should be the environment used to train and deploy prod model artifacts.

# Limit write access in prod

By design, so long as a data scientist has an `OPSML_TRACKING_URI` they should be able to read and write objects to the `Opsml` server. However, we usually don't want anyone to write/update a prod artifact from a non-prod environment. As an added measure of security, only requests coming from a prod environment will be allowed to write/update prod artifacts (anything can be read). This is accomplished through a `verify_token` dependency that checks for an `OPSML_PROD_TOKEN` token in your request and matches it to the `OPSML_PROD_TOKEN` in the prod environment. **Note** This is only checked if the `APP_ENV` is set to 'production'.

For this functionality to work you will need to set `OPSML_PROD_TOKEN` env var in both the **production** compute environment that your data scientists use to train models and in the **production** environment that hosts the `Opsml Server`. Once these are set, `Opsml` will take care of the rest. It is also recommended that you use `APP_ENV` as the env var that specifies the current environment (dev, staging, production).