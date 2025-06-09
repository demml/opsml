# Tools

Out of the box, Opsml allows you to create tool configurations within you pyproject.toml file to help simplify some workflows. Currently, tool configuration support:

## **Global Default Variables**

- Define global attributes that apply to all cards created in the project.
- Supports `space`, `name`, and `version`.

### Example

```toml
[tool.opsml.default]
space = "space"
name = "my-card"
```

Now when you create a card, it will automatically use these values unless overridden.

```python
modelcard = ModelCard( # (1)
    interface=model_interface,
    tags=["foo:bar", "baz:qux"],
    datacard_uid=datacard.uid,
)

model_registry.register_card(modelcard)
```

1. `space` and `name` are automatically set to "space" and "my-card" respectively, as defined in the `pyproject.toml` file.

## **Global Registry Variables**

- A more granular way to define registry/card-specific variables.
- Allows you to specify `space`, `name`, and `version` for each registry.
- Each line defines a registry type (e.g., model, prompt) and its associated variables.

### Example

```toml
[tool.opsml.registry]
model = { space = "opsml", name = "my-model" }
prompt = { space = "opsml", name = "my-prompt" }
```

```python
modelcard = ModelCard( # (1)
    interface=model_interface,
    tags=["foo:bar", "baz:qux"],
    datacard_uid=datacard.uid,
)

model_registry.register_card(modelcard)


card = PromptCard(
    prompt=Prompt( # (2)
        model="gpt-4o",
        provider="openai",
        user_message="Provide a brief summary of the programming language $1.",
        system_message="Be concise, reply with one sentence.",
    ),
)

prompt_registry.register_card(card)

```
1. The modelcard will automatically use the space "opsml" and name "my-model" as defined in the `pyproject.toml` file for the model registry.
2. The prompt card will automatically use the space "opsml" and name "my-prompt" as defined in the `pyproject.toml` file for the prompt registry.


## **Card Decks**
A Card Deck is a collection of cards that can be used to group related cards together. This allows you to:

1. Manage multiple cards as a single entity, making it easier to deploy and maintain.
2. Access a specific card in the deck by its alias. This allows you to use the card's interface to perform operations, such as making predictions with a model.
Currently, you can create a card deck through the client API or through a tool configuration in your `pyproject.toml` file.
3. Lock and update application ML artifacts in a more declarative way.

More information on card decks can be found in the [Card Decks documentation](../automation/carddeck.md).


```toml
[[tool.opsml.deck]]
space = "space"
name = "name1"
version = "1"
write_dir = "opsml_app/app1"
cards = [
    {alias = "my_prompt", space="space", name="prompt", version = "1.*", type = "prompt"}, # (1)
    {alias = "my_model", space="space", name="model", version = "1.*", type = "model"} # (2)
]
```

1. The first card in the deck is a prompt card with the alias "my_prompt", which can be accessed using this alias.
2. The second card in the deck is a model card with the alias "my_model", which can also be accessed using this alias.

### CardDeck Arguments

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**space**</span>       | The space to associate the CardDeck with  |
| <span class="text-alert">**name**</span>  | The name to give the CardDeck |
| <span class="text-alert">**version**</span> | The version of the CardDeck. This is automatically updated like other card types |
| <span class="text-alert">**write_dir**</span> | The optional directory where the CardDeck will be written to when `opsml install` is run |
| <span class="text-alert">**cards**</span> | A list of cards in the deck, each defined as an inline table. More information on accepted arguments is below |

### Card Arguments
| Argument     | Required | Description    |
| -----------  | -------- | ------------------------------------ |
| <span class="text-alert">**alias**</span> | Yes | The alias to use for the card in the deck. This is how you will access the card in the deck |
| <span class="text-alert">**space**</span> | Yes | The space to associate the card with. This is used to identify the card in the registry |
| <span class="text-alert">**name**</span> | Yes | The name to give the card |
| <span class="text-alert">**version**</span> | No | An optional version for the card. This works similar to other card types. For example "1.*" will match any 1.x version |
| <span class="text-alert">**type**</span> | Yes | The type of card. This is used to identify the card in the registry. Currently supported types are "model", "prompt", "data"|
| <span class="text-alert">**drift**</span> | No | An optional drift configuration for model cards. This allows you to specify drift profiles, whether to deactivate other models, and the drift profile status. More information below. |

### Drift Configuration
| Argument     | Required | Description |
| ----------- | -------- | ------------------------------------ |
| <span class="text-alert">**active**</span> | No | Whether to activate the drift profile when the deck is loaded. Defaults to `false` |
| <span class="text-alert">**deactivate_others**</span> | No | Whether to deactivate previous model version profiles when this model is activated. Defaults to `false` |
| <span class="text-alert">**drift_type**</span> | Yes | A list of drift profile types to load when the deck is loaded |


### Example Drift Configuration
**Note** - TOML does not currently support multi-line inline tables. In the future, this may change to allow for more complex configurations/better formatting.

```toml
[[tool.opsml.deck]]
type = "deck"
space = "space"
name = "name2"
version = "1"
write_dir =  "opsml_app/app2"
cards = [
    {alias = "my_prompt", space="space", name="prompt", version = "1.*", type = "prompt"},
    {alias = "my_model", space="space", name="model", version = "1.*", type = "model", drift = { active = true, deactivate_others = false, drift_type = ["custom", "psi"] }}
]
```

### Locking a CardDeck
One of the main benefits of defining a `CardDeck` within your `pyproject.toml` file is the ability to lock the deck, which will do one of the following:

- If the deck does not exist, it will create the deck and generate an `opsml.lock` file that contains the decks card configuration and dependencies.
- If the deck already exists, it will update the deck with the latest card configuration and dependencies (based on space, name and version arguments), and update the `opsml.lock` file accordingly.

### Installing a CardDeck
Once you have an `opsml.lock` file, you can install the deck and all of its artifacts by running the following command:

```bash
opsml install
```

You can now load the CardDeck directly from this path. More information on loading a CardDeck can be found in the [Card Decks documentation](../automation/carddeck.md#load-from-path).