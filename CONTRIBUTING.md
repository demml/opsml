# Contributing to demml/opsml

## Welcome
Hello! We're glad and grateful that you're interested in contributing to opsml :tada:! Below you will find the general guidelines for setting up your environment and creating/submitting `pull requests` and `issues`.

## Table of contents

- [Contributing to demml/opsml](#contributing-to-demmlopsml)
  - [Welcome](#welcome)
  - [Table of contents](#table-of-contents)
  - [Submitting Issues](#submitting-issues)
  - [Pull Requests](#pull-requests)
    - [Environment Setup](#environment-setup)
    - [Contributing Changes](#contributing-changes)
    - [Community Guidelines](#community-guidelines)
  - [_Thank you!_](#thank-you)


## Submitting Issues

Documentation issues, bugs, and feature requests are all welcome! We want to make opsml as useful as possible, so please let us know if you find something that doesn't work or if you have an idea for a new feature. To create a new issue, click [here](https://github.com/demml/opsml/issues/new/choose) and select the appropriate issue template.

## Pull Requests 

There's always something to improve in opsml, and we want to make it as easy as possible for you to contribute. We welcome all contributions, big or small, and we appreciate your help in making opsml better. The following sections will guide you through the process of contributing to opsml.

### Environment Setup

Depending on what area you're interested in contributing to, you may need to set up your environment differently. Opsml primarily uses a Rust backend and exposes a Python API via PyO3. For python environment management, OpsML leverages [uv](https://docs.astral.sh/uv/). For the frontend, opsml exposes a static SPA built with [Svelte](https://svelte.dev/) and [SvelteKit](https://svelte.dev/docs/kit/introduction).

1. Install Rust and Cargo by following the instructions [here](https://www.rust-lang.org/tools/install).
2. Install uv by following the instructions [here](https://docs.astral.sh/uv/getting-started/installation/).
3. Install python 3.10 or higher (e.g. `uv python install 3.12`).
4. Install docker (needed for postgres and mysql unit tests)
5. (Optional for UI contributions) Make sure npm and [pnpm](https://pnpm.io/installation) are installed on your system.

**Ensure everything works**:

From the root directory of the project, run the following commands to ensure everything is working correctly:

```console
$ make start.server
```

This should start the OpsML server, after which you should be able to access the UI on your localhost. The following will shutdown the server:

```console
$ make stop.server
```

To make sure the python client is working, run the following commands:

```console
$ cd py-opsml
$ make setup.project
$ make test.unit
```

The above will cd into the py-opsml directory, setup the python environment, build the python wheel and run the unit tests.

** You're now ready to start contributing! **

Feel free to explore more of the makefile and codebase to get a better sense of how we run some of our tests and lints, but the above commands should be enough to get you started.

### Contributing Changes
1. Create a new branch for your addition
   * General naming conventions (we're not picky):
      * `/username/<featureName>`: for features
      * `/username/<fixName>`: for general refactoring or bug fixes
2. Test your changes:
   - Testing Rust changes:
     - make sure you are in the `opsml` directory
     - run `make format` to format the code
     - run `make lints` to run the linter
     - run `make test.unit` to run util, sql, and server-side storage tests
   - Testing Python changes:
     - make sure you are in the `py-opsml` directory
     - run `make setup.project` to setup the python environment and build the python wheel
     - run `make format` to format the code
     - run `make lints` to run the linter
     - run `make test.unit` to run the python unit tests
3. Submit a Draft Pull Request. Do it early and mark it `WIP` so a maintainer knows it's not ready for review just yet. You can also add a label to it if you feel like it.
4. Move the `pull_request` out of draft state.
   * Make sure you fill out the `pull_request` template (included with every `pull_request`)
5. Request review from one of our maintainers (this should happen automatically via `.github/CODEOWNERS`). 
6. Get Approval. We'll let you know if there are any changes that are needed. 
7. Merge your changes into opsml!


### Community Guidelines
  1. Be Kind
    - Working with us should be a fun learning opportunity (for all parties!), and we want it to be a good experience for everyone. Please treat each other with respect.  
    - If something looks outdated or incorrect, please let us know! We want to make opsml as useful as possible. 
  2. Own Your Work
     * Creating a PR for opsml is your first step to becoming a contributor, so make sure that you own your changes. 
     * Our maintainers will do their best to respond to you in a timely manner, but we ask the same from you as the contributor. 

## _Thank you!_