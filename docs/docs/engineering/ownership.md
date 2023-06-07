# Ownership

In many organizations there is often a separation of concerns between data science and engineering when it comes to data science tooling and infrastructure. Thus, with something like `Opsml` it's appropriate to think "who owns what?" or "where does data science and engineering fit into the lifecycle, use, and management of a system like this?". The goal of `Opsml` is to provide an interface into infrastructure that data scientists use and engineering owns/controls. The diagram below is one example of this separation of concerns.

## **Architecture of Opsml Proxy Setup**

<p align="center">
  <img src="../../images/opsml-example-arch.png" width="1419" height="845"/>
</p>

### General Setup

**Note** - This is an example setup to give an overview of the serparation between data science and engineering

`Opsml` is packaged and deployed as a proxy system where a server is set up and exposed via a callable api that data scientists set as an environment variable (OPSML_TRACKING_URI). When data scientists use `Opsml` they will interact with the server through a client API that is automatically configured when `Opsml` is loaded in python.

#### Parts Owned by Engineering

- `Opsml` server that is packaged into a docker container and deployed through K8s
- Storage system (local or cloud) that will be used to store `ArtifactCard` artifacts (models, data, figures, etc.) 
- Database that will be use to store `ArtifactCard` metadata. This will typically be a mysql or postgresql database
- K8s and compute infrastructure for hosting applications
- CI/CD build process

#### Other Considerations

- In this scenario it is expected that the infrastructure hosting the `Opsml` server is also responsible for authentication and security. As an example, the host system may be placed on an internal network that is only accessible via authentication through a VPN. `Opsml` was built to be an ML tooling interface, not a security system. Thus, security should be configured on the host system.
- Credentilialing for external systems (storage, databases, etc.) should also be configured and embedded in the environment that hosts the `Opsml` server. This enables engineering to limit and control the credentials needed for `Opsml`. It also eliminates the need for data scientists to have to specify credentials when working with `Opsml` (apart for security authentication).

### Scenario 1: DS Workflows

This scenario covers the typical data science workflow and tasks that include exploratory analysis, model training and model evaulation. As part of this workflow, a data scientist will produce various `ArtifactCards` and store their attributes/metadata through client/server communication.

### Scenario 2: Model Deployment

In this scenario, a data scientist or ml engineer creates the custom api logic for their model ([FastApi](https://fastapi.tiangolo.com/) for example) and specifies resources to deploy in a custom configuration or specification file. For this example, assume the engineering team has set up an automated process whereby changes to the configuration file and push/tags trigger a CI/CD process that builds and serves a new model api. Upon build kickoff, the model specified in the configuration file is downloaded from the `Opsml` server and packaged along with the api code into a docker container. This docker container is then deployed on K8s where the api is served and ready for requests.
