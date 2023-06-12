Cards (aka Artifact Cards) are one of the primary interfaces for working with `Opsml`.

<p align="center">
  <img src="../../images/card-flow.png" width="457" height="332"/>
</p>

## Card Types

- `DataCard`: Card used to store data-related information (data, dependent variables, feature descriptions, split logic, etc.)
- `ModelCard`: Card used to store trained model and model information
- `RunCard`: Stores artifact and metric info related to Data, Model, or Pipeline cards.
- `PipelineCard`: Stores information related to a training pipeline and all other cards created within the pipeline (Data, Run, Model)
- `ProjectCard`: Stores information related to unique projects. You will most likely never interact with this card directly.


## Registries

Each card type is associated with a specific registry (`DataCard` with data registry, `ModelCard` with model registry, etc.), and registries can be used to `list`, `load` and `register` cards.

### Listing Cards
Return either a list of dictionaries or a dataframe containing card metadata. 
: Required Args:
  
    - Name: Name of card *(Optional)*
    - Team: Team associated with card *(Optional)*
    - Version: Version of Card *(Optional)*
    - uid: Uid of card *(Optional)*
    - info: `CardInfo` dataclass that can be used in place of Name, Team, Version and Uid
    - limit: Limit result
    - as_dataframe: Returns a dataframe if true else list of dictionaries

  Example:

  ```python

  from opsml.registry import CardRegistry

  registry = CardRegistry(registry_name="model") # can be "data", "model", "run", "pipeline

  # examples
  registry.list_cards() 
  # will list all cards in registry

  registry.list_cards(limit=10) 
  # will list cards and limit the result to 10
  
  registry.list_cards(name="linear-reg")
    # list all cards with name "linear-reg"
  
  registry.list_cards(name="linear-reg", team="opsml") 
  # list all cards with name "linear-reg" with team "opsml"
  
  registry.list_cards(name="linear-reg", team="opsml", version="1.0.0") 
  # list card with name "linear-reg" with team "opsml" and version 1.0.0

  registry.list_cards(name="linear-reg", team="opsml", version="1.*.*") 
  # list cards with name "linear-reg" with team "opsml" and major version of "1"

  registry.list_cards(name="linear-reg", team="opsml", version="^2.3.4") 
  # list card with name "linear-reg" with team "opsml" and latest version < 3.0.0

  registry.list_cards(name="linear-reg", team="opsml", version="~2.3.4") 
  # list card with name "linear-reg" with team "opsml" and latest version < 2.4.0

  registry.list_cards(uid=uid, as_dataframe=False)
  # list card by uid
  # will return a list of dictionaries instead of a dataframe

  ```

### Loading Cards
Load an Artifact card from a registry. 
: Required Args:
  
    - Name: Name of card *(Optional)*
    - Team: Team associated with card *(Optional)*
    - Version: Version of Card *(Optional)*
    - uid: Uid of card *(Optional)*
    - info: `CardInfo` dataclass that can be used in place of Name, Team, Version and Uid


```python

  from opsml.registry import CardRegistry
  model_registry = CardRegistry(registry_name="model")

  example_record = model_registry.list_cards(name="linnerrud", as_dataframe=False)[0]

  model_card = model_registry.load_card(uid=example_record.get("uid"))
  print(model_card.version)
  #> 1.0.0

```

### Registering a Card
Register a card to a registry 
: Required Args:
  
    - card: Card to register
    - version_type: Type of version increment. Can be "major", "minor" and "patch" *(Optional)*
    - save_path: Specific path to save to in root opsml folder if default are not preferred *(Optional)*


```python

  from opsml.registry import CardRegistry

  model_registry = CardRegistry(registry_name="model")

  model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="linear-reg",
        team="opsml",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
    )

  example_record = model_registry.register_card(card=model_card)
  print(model_card.version)
  #> 1.0.0
  
```
