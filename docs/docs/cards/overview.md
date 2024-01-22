Cards (aka ArtifactCards) are one of the primary data structures for working with `Opsml` that contain both data and model interface objects as well as associated metadata. `ArtifactCards` are stored in registries and can be used to track and version data and models.

<p align="center">
  <img src="../../images/card-flow.png" width="457" height="332"/>
</p>

## Card Types

- `DataCard`: Card used to store data-related information (``, dependent variables, feature descriptions, split logic, etc.)
- `ModelCard`: Card used to store trained model and model information
- `RunCard`: Stores artifact and metric info related to Data, Model, or Pipeline cards.
- `ProjectCard`: Stores information related to unique projects. You will most likely never interact with this card directly.

## Registries

Each card type is associated with a specific registry (`DataCard` with data registry, `ModelCard` with model registry, etc.), and registries can be used to `list`, `load` and `register` cards.

### Card Information

You'll notice when working with `ArtifactCards` and `CardRegistries` that there are a few common arguments that are always required. These arguments are:

- **name**: Name of card
- **repository**: Repository associated with card
- **contact**: Contact information for card

These arguments are required for card registration and can be supplied through named arguments or through a `CardInfo` dataclass.

`CardInfo` is a helper class that can be used to store these arguments so you don't need to make repetitive calls. In addition, the `CardInfo` class allows you to set `runtime` environment variables through a `set_env()` method. This will allow to create cards without having to specify `name`, `repository` and/or `contact`. Examples are below.

#### Example of named arguments

```python hl_lines="1 6-9"
from opsml import DataCard

# skip data interface logic
...

DataCard(
  name="linnerud", 
  repository="opsml", 
  contact="mlops.com", 
  interface=data_interface
  )
```

#### Example of CardInfo

```python hl_lines="1 3 8-9"
from opsml import DataCard, CardInfo

info = CardInfo(name="linnerud", repository="opsml", contact="mlops.com")

# skip data interface logic
...

DataCard(
  info=info,
  interface=data_interface
  )
```

#### Example of Runtime Env Vars

```python hl_lines="1 3 8"
from opsml import DataCard, CardInfo

info = CardInfo(name="linnerud", repository="opsml", contact="mlops.com").set_env()

# skip data interface logic
...

DataCard(interface=data_interface)
```

### Name Uniqueness

When registering cards, `Opsml` will check to see if a card with the same name, repository and version already exists. Therefore, name uniqueness is guaranteed at the `repository/name` level. Thus, different repositories can share cards with the same name.

### Listing Cards
Returns a list of dictionaries. 
: Required Args:
  
    - Name: Name of card *(Optional)*
    - repository: repository associated with card *(Optional)*
    - Version: Version of Card *(Optional)*
    - uid: Uid of card *(Optional)*
    - info: `CardInfo` dataclass that can be used in place of Name, repository, Version and Uid
    - limit: Limit result

  Example:

  ```python

  from opsml import CardRegistry

  registry = CardRegistry(registry_name="model") # can be "data", "model", "run", "pipeline

  # examples
  registry.list_cards() 
  # will list all cards in registry

  registry.list_cards(limit=10) 
  # will list cards and limit the result to 10
  
  registry.list_cards(name="linear-reg")
    # list all cards with name "linear-reg"
  
  registry.list_cards(name="linear-reg", repository="opsml") 
  # list all cards with name "linear-reg" with repository "opsml"
  
  registry.list_cards(name="linear-reg", repository="opsml", version="1.0.0") 
  # list card with name "linear-reg" with repository "opsml" and version 1.0.0

  registry.list_cards(name="linear-reg", repository="opsml", version="1.*.*") 
  # list cards with name "linear-reg" with repository "opsml" and major version of "1"

  registry.list_cards(name="linear-reg", repository="opsml", version="^2.3.4") 
  # list card with name "linear-reg" with repository "opsml" and latest version < 3.0.0

  registry.list_cards(name="linear-reg", repository="opsml", version="~2.3.4") 
  # list card with name "linear-reg" with repository "opsml" and latest version < 2.4.0

  registry.list_cards(uid=uid)
  # list card by uid
  ```

### Registering a Card
Register a card to a registry 
: Required Args:
  
    - card: Card to register
    - version_type: Type of version increment. Can be "major", "minor" and "patch" *(Optional)*
    - save_path: Specific path to save to in root opsml folder if default are not preferred *(Optional)*


Example:

```python hl_lines="1 3 16"

from opsml import CardRegistry

model_registry = CardRegistry(registry_name="model")

# skipping ModelInterface logic
...

model_card = ModelCard(
      interface=model_interface,
      name="linear-reg",
      repository="opsml",
      contact="mlops.com",
      datacard_uid=data_card.uid,
  )

example_record = model_registry.register_card(card=model_card)
print(model_card.version)
#> 1.0.0
  
```

### Loading Cards
Load an Artifact card from a registry. 
: Required Args:
  
    - Name: Name of card *(Optional)*
    - repository: repository associated with card *(Optional)*
    - Version: Version of Card *(Optional)*
    - uid: Uid of card *(Optional)*
    - info: `CardInfo` dataclass that can be used in place of Name, repository, Version and Uid

Example:

```python hl_lines="1-2 6"
from opsml import CardRegistry
model_registry = CardRegistry(registry_name="model")

example_record = model_registry.list_cards(name="linnerrud", )[0]

model_card = model_registry.load_card(uid=example_record.get("uid"))
print(model_card.version)
#> 1.0.0
```

### Update Cards

You can also update cards

```python hl_lines="8"
from opsml import CardRegistry
model_registry = CardRegistry(registry_name="model")

# skipping card logic
...

card.contact = "new_contact"
model_registry.update_card(card)
```


### Deleting Cards

In the event you need to delete a card, there's a built in `delete_card` method.

```python hl_lines="7"
from opsml import CardRegistry
model_registry = CardRegistry(registry_name="model")

# skipping card logic
...

model_registry.delete_card(card)
```

::: opsml.CardRegistry
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3