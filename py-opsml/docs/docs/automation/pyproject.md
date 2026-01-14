# Tools

Out of the box, Opsml allows you to create tool configurations within your pyproject.toml file to help simplify some workflows. Currently, tool configurations support:

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
        messages="Provide a brief summary of the programming language $1.",
        system_instructions="Be concise, reply with one sentence.",
    ),
)

prompt_registry.register_card(card)

```
1. The modelcard will automatically use the space "opsml" and name "my-model" as defined in the `pyproject.toml` file for the model registry.
2. The prompt card will automatically use the space "opsml" and name "my-prompt" as defined in the `pyproject.toml` file for the prompt registry.