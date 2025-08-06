# Technical Component Specification: ServiceCard

## Overview
The ServiceCard is a primary interface for managing collections of `Cards` in `OpsML`. It's primary use-case is at the application-level where a user may want to attach multiple cards to a given service (e.g. an api). For instance, if a user has an api that requires 4 different models or an agentic workflow that requires 5 different prompts, the `ServiceCard` can greatly streamline managing and loading these cards within a service. Similar to all cards, a `ServiceCard` is versioned and can be registered with the OpsML registry. This allows for easy tracking of changes to the service card over time.

## Key Changes
- Introduction of the ServiceCard struct and python class for managing collections of different card types
- Support for saving and loading complete card collections with a single operation
- Card aliasing system for convenient access to individual cards
- Implementation of Pythonic interfaces for iteration and dictionary-like access
- Serialization/deserialization support for persistence
- CLI integration for registering/locking and downloading artifacts

## Implementation Details

### Core Components

#### ServiceCard
```rust
#[pyclass]
#[derive(Debug)]
pub struct ServiceCard {
    #[pyo3(get, set)]
    pub space: String,
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub version: String,
    #[pyo3(get, set)]
    pub uid: String,
    #[pyo3(get, set)]
    pub created_at: DateTime<Utc>,
    #[pyo3(get)]
    pub cards: CardList,
    #[pyo3(get)]
    pub opsml_version: String,
    #[pyo3(get, set)]
    pub app_env: String,
    #[pyo3(get)]
    pub is_card: bool,
    #[pyo3(get)]
    pub registry_type: RegistryType,
    // Holds the actual card objects (ModelCard, DataCard, etc.)
    pub card_objs: HashMap<String, PyObject>,
}
```

The `ServiceCard` struct contains the following fields:
- `space`: The space to which the service card belongs
- `name`: The name of the service card
- `version`: The version of the service card
- `uid`: A unique identifier for the service card
- `created_at`: The timestamp when the service card was created
- `cards`: A collection of cards (CardList)
- `opsml_version`: The version of OpsML used
- `app_env`: The application environment (e.g., production, development)
- `is_card`: A boolean indicating if the service card is a card itself
- `registry_type`: The type of registry (e.g., Model, Data, Service)
- `card_objs`: A HashMap holding the actual card objects (e.g., ModelCard, DataCard)

#### CardList
```rust
#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct CardList {
    #[pyo3(get)]
    pub cards: Vec<Card>,
}
```

The `CardList` is a holder for Card entries in a `ServiceCard` and implements Pythonic dunders for ergonomic access via python:
- `__iter__` for iteration over cards
- `__len__` to get collection size
- `__getitem__` for index-based access
- IntoIterator for Rust-side iteration

#### Card
```rust
#[pyclass(eq)]
#[derive(Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Card {
    #[pyo3(get, set)]
    pub space: String,
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub version: String,
    #[pyo3(get, set)]
    pub uid: String,
    #[pyo3(get, set)]
    pub registry_type: RegistryType,
    #[pyo3(get, set)]
    pub alias: String,
}
```
The Card struct represents references to actual card objects and can be created in multiple ways:
- From an existing/registered card object
- By specifying a registry type and identifier information (space, name, version, uid, etc.)
  - In this case, a user must supply (space + name + version (optional) + registry_type) or (uid + registry_type) to create a card reference.

### How It Works

#### Loading a ServiceCard and Cards
```rust
pub fn load<'py>(
    &mut self,
    py: Python<'py>,
    load_kwargs: Option<HashMap<String, Bound<'_, PyAny>>>,
) -> PyResult<()>
```

As with all cards, the `ServiceCard` is loaded lazily. The `load` method takes a dictionary of keyword arguments for each card by their `alias`. The keyword arguments are passed to the respective card's `load` method. Note - this method can only be called after the `ServiceCard` has been loaded from the registry.

#### Download Artifacts
```rust
#[pyo3(signature = (path=None))]
pub fn download_artifacts(&mut self, py: Python, path: Option<PathBuf>) -> PyResult<()>
```

Downloads all artifacts associated with all cards in the service to the specified path with the structure:
```
{base_path}/
├── card.json                # ServiceCard metadata
├── {alias1}/                # Files for the first card
│   └── card.json            # First card metadata
├── {alias2}/                # Files for the second card
│   └── card.json            # Second card metadata
└── ...
```

Note: While this method is publicly available for convenience, there is no need to call it directly when loading Card artifacts as the `load` method will automatically download all artifacts to their respective paths.

#### Dictionary-like Access
```rust
pub fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<Bound<'py, PyAny>>
```

Enables Python-side dictionary-style access to cards using their aliases:
```python
# Access a model card with alias "model"
model = service["model"]
```

### Serialization Support

The ServiceCard includes custom serialization/deserialization implementations to handle:
- Python object references that can't be directly serialized
- Restoration of object state when loading from JSON
- Proper handling of PyObject references in a memory-safe way

### Integration with OpsML Card System

The ServiceCard implements the `OpsmlCard` trait
```rust
impl OpsmlCard for ServiceCard {
    fn get_registry_card(&self) -> Result<CardRecord, CardError> {
        self.get_registry_card()
    }
    // Additional trait methods...
}
```

This enables the ServiceCard to be created and registered directly from Rust. This trait is utilized when leveraging the opsml cli.

## Usage Examples

### Python-side Usage

```python
# Creating a new ServiceCard
registry = CardRegistry(RegistryType.Service)

service = ServiceCard(
    space="test",
    name="test",
    cards=[
        Card(
            alias="model",
            uid=modelcard.uid,
            registry_type=RegistryType.Model,
        ),
        Card(
            alias="prompt",
            card=promptcard,  # Direct card reference
        ),
    ],
)

# Registration
registry.register_card(service)

# Accessing cards by alias
model = service["model"]
data = service["prompt"]

# Loading ServiceCard from the registry
loaded_service = registry.load_card(uid=service.uid)

# Load card
loaded_service.load()

# Load card example with kwargs (pass modelkwargs to load onnx)
loaded_service.load({"model": ModelLoadKwargs(load_onnx=True)})


# Loading from filesystem (assume artifacts are already downloaded to path)
loaded_service = ServiceCard.from_path("my_service")

loaded_service["model"].model # access the model
loaded_service["prompt"].prompt # access the prompt
```

## Performance Considerations

1. **Memory Management**
   - PyObject references are tracked and managed through PyO3's memory management
   - The `__traverse__` and `__clear__` methods ensure proper garbage collection.


2. **Storage Efficiency**
   - Only references to cards are stored in the ServiceCard metadata
   - Actual card objects are loaded/downloaded on demand
   - PyObjects are bound to python objects to avoid unnecessary copies

---
*Version: 1.0*  
*Last Updated: 2025-07-08*  
*Author: Steven Forrester*