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

**Listing Cards**
Return either a list of dictionaries or a dataframe containing card metadata. 
: Required Args:
  
    - Name: Name of card *(Optional)*
    - Team: Team associated with card *(Optional)*
    - Version: Version of Card *(Optional)*
    - uid: Uid of card *(Optional)*

    Example:

    ```python

    from opsml.registry import CardRegistry

    registry = CardRegistry(registry_name="model") # can be "data", "model", "run", "pipeline

    # examples
    registry.list_cards() 
    # will list all cards in registry
    
    registry.list_cards(name="linear-reg")
     # list all cards with name "linear-reg"
    
    registry.list_cards(name="linear-reg", team="opsml") 
    # list all cards with name "linear-reg" with team "opsml"
    
    registry.list_cards(name="linear-reg", team="opsml", version="1.0.0") 
    # list card with name "linear-reg" with team "opsml" and version 1.0.0

    registry.list_cards(name="linear-reg", team="opsml", version="1.*.*") 
    # list card with name "linear-reg" with team "opsml" and major version of "1"

    registry.list_cards(name="linear-reg", team="opsml", version="^2.3.4") 
    # list card with name "linear-reg" with team "opsml" and major version of ""

    registry.list_cards(uid=uid, as_dataframe=False) # will return a list of di
    # list card by uid
    # will return a list of dictionaries instead of a dataframe


    ```



