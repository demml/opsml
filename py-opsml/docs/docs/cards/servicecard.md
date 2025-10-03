# ServiceCard

Just like you can create cards, you can also create a service of cards called a `ServiceCard`. The most important benefit of a `ServiceCard` is that is allows you to create a collection of cards that can be loaded and used together. 

A prime example of this is in model apis where you may need to load more than one model, or agentic workflows that are associated with more than one prompt. By using a `ServiceCard`, you can group these cards together and load them all at once (with a few extra nice features that we'll get into).

## Example Usage (Details below)

### Create a ServiceCard
```python
service = ServiceCard(
    space="opsml-space",
    name="opsml-service",
    cards=[
        Card(
            alias="model1",
            uid=modelcard1.uid,
            registry_type=RegistryType.Model,
        ),
        Card(
            alias="model2",
            uid=modelcard2.uid,
            registry_type=RegistryType.Model,
        ),
    ],
)
registry.register_card(service)
```

### Using a ServiceCard in FastAPI
```python

@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    logger.info("Starting up FastAPI app")

    fast_app.state.service = service = ServiceCard.from_path( # (1)
        path=settings.card_service_path
        ) 
    yield

    logger.info("Shutting down FastAPI app")
    
    # Shutdown the service card
    fast_app.state.service = None


app = FastAPI(lifespan=lifespan)

@app.post("/predict_with_model1", response_model=Response)
async def predict_model_1(request: Request, payload: PredictRequest) -> Response:
    card = cast(ModelCard, request.app.state.service["model1"]) # (2)

    prediction= card.interface.model.predict(payload.to_numpy())

    return Response(prediction=prediction[0])

@app.post("/predict_with_model2", response_model=Response)
async def predict_model_2(request: Request, payload: PredictRequest) -> Response:
    card = cast(ModelCard, request.app.state.service["model2"])

    prediction= card.interface.model.predict(payload.to_numpy())

    return Response(prediction=prediction[0])
```

1. Load the `ServiceCard` and it's components directly from a path after downloading with the Opsml CLI
2. Access a specific card in the service by its alias. This allows you to use the card's interface to perform operations, such as making predictions with a model.

Currently you can create a service card through the client api or through a tool configuration in your `pyproject.toml` file.

## Create a Service

### API
Just like all other cards, you can think of a `ServiceCard` as just another card (even though it is a collection of cards). As such, all services are registered through the ServiceCard `CardRegistry`.

```python
from opsml import ServiceCard, Card, RegistryType

registry = CardRegistry(RegistryType.Service)

service = ServiceCard(
    space="opsml-space",
    name="opsml-service",
    cards=[
        Card(
            alias="model1",
            uid=modelcard1.uid,
            registry_type=RegistryType.Model,
        ),
        Card(
            alias="model2",
            uid=modelcard2.uid,
            registry_type=RegistryType.Model,
        ),
    ],
)
registry.register_card(service)
```

In the above example, we create a `ServiceCard` with two cards, `model1` and `model2`, each referencing a `ModelCard` that has **already been registered** by its unique identifier (UID). The service is then registered in the `CardRegistry` under `RegistryType.Service`.

### Service Specification and CLI

One core area of focus for OpsML `v3` is tighter integration into the workflows developers use to build their applications. Often, developers use configuration files to manage dependencies and application settings/resources. To that end, opsml `v3` introduces a service specification that allows developers to define a service (API, MCP, Agent) through a YAML file. So instead of having to write code to create a service, you can define it in a YAML file and use the OpsML CLI to create, lock, update, and install the service and its associated cards/metadata.

#### See it in action

Create an `opsmlspec.yaml` file that defines your service and its cards. These could be cards that are produced from your training pipeline or cards that are already in the registry.

```yaml
name: recommendation-api # (1)
space: data-science
type: Api

service:
  version: 1.0.0
  write_dir: opsml_service
  cards:
    - alias: prompt # (2)
      space: data-science
      name: recommendation-prompt
      version: 1.*
      type: prompt

    - alias: recommender # (3)
      space: data-science
      name: recommender-model
      version: 1.*
      type: model

    - alias: ranker # (4)
      space: data-science
      name: recommender-ranker
      version: 1.*
      type: model
      drift:
        active: true
        deactivate_others: true
        drift_type: 
          - custom
          - psi
```

1. Our service is going to be a hybrid system that involves traditional machine learning models and an agentic piece that requires the use of a prompt.
2. The prompt card that will be used by the agentic component of the service.
3. The main recommender model that will provide recommendations based on user input.
4. A ranking model that will be used to rank the recommendations provided by the recommender model. This model also has drift detection enabled to monitor for changes in data distribution over time.

After you define your `ServiceCard` in the `opsmlspec.yaml`, you can run `opsml lock`, which will create an `opsml.lock` file that will contain the resolved versions of the cards in the service. You can then run `opsml install service` to install the service and its cards into your application.
   
???tip "Naming"
    `opsmlspec.yaml` is just a standard convention for naming the spec file. You can name it whatever you want so long as its either a `yml` or `yaml` file and you provide the file path when running the CLI commands. See `opsml lock --help` for more details.

### Full Specification

Here is the full specification for the `opsmlspec.yaml` file:

| Field         | Type                       | Required | Description                                                                                   |
|---------------|----------------------------|----------|-----------------------------------------------------------------------------------------------|
| `name`        | `string`                   | Yes      | The name of the service.                                                                      |
| `space` or `team` | `string`               | Yes      | The space or team this service belongs to. Use `space` for general use, `team` for team-based.|
| `type`        | `Api` \| `Mcp` \| `Agent`  | Yes      | The type of service. Must be one of: `Api`, `Mcp`, or `Agent`.                               |
| `metadata`    | object                     | No       | Additional metadata about the service. See [Metadata fields](#metadata-fields) below.         |
| `service`     | object                     | No       | Service configuration. See [Service fields](#service-fields) below.                          |
| `deploy`      | list of objects            | No       | Deployment configurations. See [Deployment fields](#deployment-fields) below.                |

#### Metadata fields

| Field         | Type         | Required | Description                                  |
|---------------|--------------|----------|----------------------------------------------|
| `description` | `string`     | Yes      | Description of the service.                  |
| `language`    | `string`     | No       | Programming language used (e.g., `python`).  |
| `tags`        | list[string] | No       | Tags for categorization/search.              |

#### Service fields

| Field       | Type                | Required | Description                                                        |
|-------------|---------------------|----------|--------------------------------------------------------------------|
| `version`   | `string`            | No       | Version of the service.                                            |
| `cards`     | list of objects     | No       | Cards included in the service. See [Card fields](#card-fields).    |
| `write_dir` | `string`            | No       | Directory to write service artifacts to.                           |
| `mcp`       | object              | No       | MCP configuration (required if `type` is `Mcp` See [MCP Config fields](#mcp-config-fields)).                   |

#### MCP Config fields

| Field         | Type           | Required | Description                                                                 |
|---------------|----------------|----------|-----------------------------------------------------------------------------|
| `capabilities`| list[string]   | Yes      | List of MCP capabilities. One or more of: `resources`, `tools`, `prompts`.  |
| `transport`   | string         | Yes      | Transport type. One of: `http`, `stdio`.                                    |


#### Card fields

| Field         | Type                | Required | Description                                                        |
|---------------|---------------------|----------|--------------------------------------------------------------------|
| `alias`       | `string`            | Yes      | Alias for referencing this card in the service.                    |
| `space`       | `string`            | No       | Space for the card (defaults to service space if omitted).         |
| `name`        | `string`            | Yes      | Name of the card.                                                  |
| `version`     | `string`            | No       | Version specifier (e.g., `1.*`).                                   |
| `type`        | `Model` \| `Prompt` \| `Service` \| `Mcp` | Yes | Registry type of the card.                                         |
| `drift`       | object              | No       | Drift detection config (only for model cards). See below.          |

**Drift fields** (only for model and prompt cards):

| Field             | Type           | Required | Description                                  |
|-------------------|----------------|----------|----------------------------------------------|
| `active`          | `bool`         | No       | Whether drift detection is active.            |
| `deactivate_others` | `bool`       | No       | Deactivate previous drift config versions if true.       |
| `drift_type`      | list[string]   | No       | Types of drift detection (e.g., `psi`, `custom`). |

#### Deployment fields

| Field         | Type                | Required | Description                                                        |
|---------------|---------------------|----------|--------------------------------------------------------------------|
| `environment` | `string`            | Yes      | Deployment environment (e.g., `development`, `production`).        |
| `provider`    | `string`            | No       | Cloud provider (e.g., `gcp`, `aws`).                              |
| `location`    | list[string]        | No       | Deployment locations/regions.                                      |
| `endpoints`   | list[string]        | Yes      | List of endpoint URLs.                                             |
| `resources`   | object              | No       | Resource requirements. See [Resources fields](#resources-fields).  |
| `links`       | map[string,string]  | No       | Related links (e.g., logging, monitoring URLs).                    |

#### Resources fields

| Field     | Type         | Required | Description                                  |
|-----------|--------------|----------|----------------------------------------------|
| `cpu`     | `integer`    | Yes      | Number of CPUs required.                     |
| `memory`  | `string`     | Yes      | Amount of memory (e.g., `16Gi`).             |
| `storage` | `string`     | Yes      | Storage required (e.g., `100Gi`).            |
| `gpu`     | object       | No       | GPU configuration. See below.                |

**GPU fields**:

| Field     | Type      | Required | Description                                  |
|-----------|-----------|----------|----------------------------------------------|
| `type`    | `string`  | Yes      | GPU type (e.g., `nvidia-tesla-t4`).          |
| `count`   | `integer` | Yes      | Number of GPUs.                              |
| `memory`  | `string`  | Yes      | GPU memory (e.g., `16Gi`).                   |

---

???tip "Yaml Spec"
    The following is the full specification in yaml
    Here is the full specification for the `opsmlspec.yaml` file:

    ```yaml
    name: my-service                # (string, required) Name of the service
    space: my-space                # (string, required) Space or use 'team' for team-based
    type: Api                      # (string, required) One of: Api, Mcp, Agent

    metadata:                      # (object, optional)
    description: "A sample service"      # (string, required)
    language: "python"                  # (string, optional)
    tags: ["ml", "production"]          # (list[string], optional)

    service:                        # (object, optional)
    version: "1.0.0"              # (string, optional)
    write_dir: "opsml_service"    # (string, optional)
    cards:                        # (list of cards, optional)
        - alias: recommender
        space: my-space
        name: recommender-model
        version: "1.*"
        type: model
        drift:                    # (object, optional, only for model cards)
            active: true
            deactivate_others: false
            drift_type: ["psi", "custom"]
        - alias: prompt
        name: prompt-card
        type: prompt

    mcp:                          # (object, optional, required if type is Mcp)
        capabilities:               # (list of strings, required)
          - resources               # One of: resources, tools, prompts
          - tools
        transport: http             # (string, required) One of: http, stdio)

    deploy:                         # (list of objects, optional)
    - environment: production     # (string, required)
        provider: aws               # (string, optional)
        location: [us-east-1]       # (list[string], optional)
        endpoints: ["https://api.example.com"]  # (list[string], required)
        resources:                  # (object, optional)
        cpu: 4                    # (integer, required)
        memory: 16Gi              # (string, required)
        storage: 100Gi            # (string, required)
        gpu:                      # (object, optional)
            type: nvidia-tesla-t4   # (string, required)
            count: 2                # (integer, required)
            memory: 16Gi            # (string, required)
        links:                      # (map[string,string], optional)
        logging: https://logs.example.com
        monitoring: https://monitor.example.com
    ```

## Using a ServiceCard
Once you have created a `ServiceCard`, you can use it in your application. To load a `ServiceCard` you can either load it directly from the registry or load if from a path where it was downloaded to.

### Downloading with the CLI

In most cases, when deploying your application, you'll want to leverage the Opsml CLI to download the service and its associated cards to a local path. This is a common pattern for containerized applications where you'll want to copy the service into the container image during the build process.

Assuming you already have a service registered and an `opsml.lock` file created, you can use the following command to download the service and its cards:

```bash
opsml install service
```

This will download the service and its cards to a local directory (by default, `./opsml_service` unless otherwise specified in the `opsmlspec.yaml` file). You can then load the service in your application using the path to the downloaded service. While Opsml gives you the flexibility to load the service as you see fit, we recommend using `AppState` in applications to manage the lifecycle of the service ([link](../deployment/overview.md#appstate)).

### Load from Registry
You can load a `ServiceCard` from the registry using the `CardRegistry`:

```python
from opsml import CardRegistry, RegistryType, ModelLoadKwargs, ServiceCard

registry = CardRegistry(RegistryType.Service)

loaded_service: ServiceCard = registry.load_card(...) # (1)
loaded_service.load() # (2)

# loading cards that require addition kwargs
loaded_service.load(load_kwargs = {"model1": ModelLoadKwargs(load_onnx=True)}) # (3)

# accessing cards in the service
card1 = loaded_service["model1"]  # (4)
```

1. Services are loaded just like any other card using a variety of arguments (space, name, version, uid, etc.)
2. Load all card artifacts and interfaces
3. Load cards with additional keyword arguments, such as loading a model in ONNX format
4. Access individual cards in the service using their aliases

### Load from Path
You can also load a `ServiceCard` from a path where it was downloaded to using `opsml install`. This is useful when you have downloaded the service using the Opsml CLI and want to use it in your application.

```python
from opsml import ServiceCard, ModelLoadKwargs

load_kwargs = {
        "model": {"load_kwargs": ModelLoadKwargs(load_onnx=True)},
    }
loaded_service = ServiceCard.from_path("path/to/service", load_kwargs=load_kwargs) # (1)
```

1. Load the `ServiceCard` from a specified path, optionally providing load arguments for specific cards. Unlike registry loading, load_from_path will load all cards and their interfaces and artifacts by default (e.g. models), so there is no need to call `load()` on the service after loading it from a path. 

### Custom Interfaces
In the case you are using a custom interface for any cards that are associated with a ServiceCard, you will need to provide the custom interface at load time.

#### Loading from Registry

```python
from opsml import CardRegistry, RegistryType, ModelLoadKwargs, ServiceCard

registry = CardRegistry(RegistryType.Service)

loaded_service: ServiceCard = registry.load_card(
        interface = {"model1": MyCustomInterface} # (1)
        ) 
loaded_service.load() 
```

1. Similar to loading other cards with a custom interface, you can provide the custom interface when loading the service from the registry. However, you will need to provide it as a dictionary mapping of alias to custom interface class.

#### Loading from Path
```python
from opsml import ServiceCard, ModelLoadKwargs

load_kwargs = {
        "model": {
            "load_kwargs": ModelLoadKwargs(load_onnx=True),
            "interface": MyCustomInterface, # (1)
        },
    }
loaded_service = ServiceCard.from_path("path/to/service", load_kwargs)
```

1. When loading from a path, you can provide the custom interface directly in the `load_kwargs` for the specific card. This allows you to use your custom interface when loading the card from the service.


For more information on how `ServiceCards` can be leveraged during application deployment, see the [Deployment](../deployment/overview.md) documentation.