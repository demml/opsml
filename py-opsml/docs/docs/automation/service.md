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


### Tool Configuration

You can also create ServiceCards through a tool configuration in your `pyproject.toml` file. This is useful for creating, locking, updating and installing ServiceCards in a more declarative way. 

To create a `ServiceCard` in your `pyproject.toml`, you can use the following format:

1. Define a [[tool.opsml.service]] section.
2. Specify the `space`, `name`, and `version` of the service.
3. Specify the `write_dir` that the service card will be written to whenever `opsml install` is run.
4. List the cards in the `cards` inline-table array, where each card is defined with its `alias`, `space`, `name`, `version`, and `type`.
5. Optionally, you can specify `drift` settings for a card if it is a model card. You can set the drift profile status, whether to deactivate other models, and the drift profiles to load when the service is loaded.

```toml
[[tool.opsml.service]]
space = "space"
name = "name1"
version = "1"
write_dir = "opsml_app/app"
cards = [
    {alias = "my_prompt", space="space", name="prompt", version = "1.*", type = "prompt"},
    {alias = "my_model", space="space", name="model", version = "1.*", type = "model"}
    {alias = "my_drift_model", space="space", name="model", version = "1.*", type = "model", drift = { active = true, deactivate_others = false, drift_type = ["custom", "psi"] }}
]
```

After you define your `ServiceCard` in the `pyproject.toml`, you can run `opsml lock` that will create an `opsml.lock` file that will contain the resolved versions of the cards in the service. You can then run `opsml install` to install the service and its cards into your application.

**NOTE:** The `opsml.lock` file is a snapshot of the current state of your service and its cards. Based on how you configure your card versions, `opsml lock` can be used to continually update the versions of the cards in your service.


## Using a ServiceCard
Once you have created a `ServiceCard`, you can use it in your application. To load a `ServiceCard` you can either load it directly from the registry or load if from a path where it was downloaded to.

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
In the case you are using a custom interface for any cards that are associated with a ServiceCard, you will need to provide the custom interface at load times.

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