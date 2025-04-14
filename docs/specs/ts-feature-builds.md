# Technical Component Specification: Builds

## Overview
As part of [pr](#), we are introducing github action workflows to build and publish OpsML artifacts. This includes the following:
- **Docker Images**: Base Docker images for the OpsML server
- **Python Wheels**: Python wheels for OpsML (with server) and OpsML client (without server)
- **Compressed Artifacts**: Compressed artifacts for OpsML (with server)


## Implementation Details

### Docker Images (OpsML Server)
As part of our goal to make OpsML an easy to use tool, it's important to provide resources that allow end-users to get up and running fast. The goal of the docker image workflows is to provide base images in a variety of formats that will allow engineering teams to pull from without having to install rust and build their own servers from source, although they can still do this if they'd like. One every release or a new version of OpsML, we will build, tag and publish docker images in a variety of formats.

#### Docker Tags

Ubuntu:

- (arm64): `demm/opsml:ubuntu-arm64-{version}`
- (amd64): `demm/opsml:ubuntu-amd64-{version}`

Alpine:

- (arm64): `demm/opsml:alpine-arm64-{version}`
- (amd64): `demm/opsml:alpine-amd64-{version}`

Scratch:

- (arm64): `demm/opsml:scratch-arm64-{version}`
- (amd64): `demm/opsml:scratch-amd64-{version}`

Debian:

- (arm64): `demm/opsml:debian-arm64-{version}`
- (amd64): `demm/opsml:debian-amd64-{version}`

Distroless:

- (arm64): `demm/opsml:distroless-arm64-{version}`
- (amd64): `demm/opsml:distroless-amd64-{version}`


### Release Artifacts (OpsML Server)
In additions to Docker images, every new release of OpsML will also include a set of release artifacts. These artifacts will be built,tagged, compressed and uploaded to the OpsML release page. The release artifacts will be built for the following targets:

- `x86_64-unknown-linux-gnu`
- `aarch64-unknown-linux-gnu`
- `aarch64-apple-darwin`
- `x86_64-apple-darwin`
- `x86_64-pc-windows-msvc`

### Python Wheels (OpsML Client)
On every new release of OpsML, we will publish two pypi libraries. `opsml` and `opsml-client`. 

The opsml version of the library comes compiled with the server features, meaning it comes with sql and server (axum) logic. While this doesn't change how a developer will use opsml, it does result in a larger python wheel. The opsml version of the library allows for developers to run opsml in both server and client mode from python. While this is not the recommended approach for all scenarios, it does make development easier in that it doesn't require a developer to spin up a server in order to save and register artifacts. 

The opsml-client version of the library is compiled without the server feature. This is the recommended library in production settings where an engineering team has already setup a server for developers to use.

### Relevant GitHub Actions

- `build-assets.yml`: Builds and publishes compressed artifacts and docker images for OpsML
- `release-server.yml`: Builds and publishes the OpsML pypi library
- `release-client.yml`: Builds and publishes the OpsML client pypi library

---

*Version: 1.0*  
*Last Updated: 2025-04-14*  
*Component Owner: Steven Forrester*