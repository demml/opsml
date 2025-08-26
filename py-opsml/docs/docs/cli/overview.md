# Command Line Interface for Opsml

`OpsML` comes pre-installed with a command line interface (CLI) that allows users to interact (list, download) with their cards an services

## Available Commands

### Command: `list`

#### Description

The `list` command is used to retrieve a list of cards from a specified registry. Users can filter the results using various arguments such as space, name, version, and more. The command supports multiple subcommands for different registry types.

#### Usage

```shell
opsml list <registry> [options]
opsml list model --space space --name name
```

#### Subcommands

- **model**: List cards from the Model registry.
- **service**: List cards from the Service registry.
- **data**: List cards from the Data registry.
- **experiment**: List cards from the Experiment registry.
- **audit**: List cards from the Audit registry.
- **prompt**: List cards from the Prompt registry.

#### Arguments for Subcommands

Each subcommand accepts the same set of arguments to filter the results:

- **space** (Optional): The name of the space to filter cards by.
- **name** (Optional): The name of the card to filter by.
- **version** (Optional): The version of the card to filter by.
- **uid** (Optional): The unique identifier of the card to filter by.
- **limit** (Optional): The maximum number of cards to return.
- **tags** (Optional): A comma-separated list of tags to filter cards by.
- **max_date** (Optional): The maximum date to filter cards by.
- **sort_by_timestamp** (Optional, default: true): Whether to sort the results by timestamp.

### Command: `get`

#### Description

The get command is used to download card artifacts from a specified registry. Users can specify the card's space, name, version, and other details to retrieve the desired artifacts. The command supports subcommands for different registry types. Currently only supports model and service subcommands.

#### Usage

```shell
opsml get <registry> [options]
```

#### Subcommands

- **model**: Download artifacts from the Model registry.
- **service**: Download artifacts from the Service registry.

#### Arguments for Subcommands
Each subcommand accepts the following arguments to specify the card to download:

- **space** (Optional): The name of the space where the card is located.
- **name** (Optional): The name of the card to download.
- **version** (Optional): The version of the card to download.
- **uid** (Optional): The unique identifier of the card to download.
- **write-dir** (Optional, default: artifacts): The directory where the downloaded artifacts will be saved.

#### Examples

##### Download a Model Card

```shell
opsml get model --space 'my_space' --name 'my_model' --version '1.0.0'
```

```shell
opsml get service --space 'my_space' --name 'my_service'
```

### Command: `lock`

#### Description

The `lock` command is used to create an `opsml.lock` file based on the service configuration specified within the pyproject.toml file. This lock file captures the state of the service and its associated cards, ensuring reproducibility and consistency.

For more information on `opsml` tool configurations, please refer to the [tool documentation](../automation/pyproject.md/#service-cards).

#### Usage

```shell
opsml lock
```

### Command: `install`

#### Description

The `install` command is used to install or download an OpsML service from an `opsml.lock` file. This command will download all artifacts specified in the lock file.

#### Usage

```shell
opsml install
```