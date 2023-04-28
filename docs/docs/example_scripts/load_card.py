from opsml.registry import CardRegistry

model_registry = CardRegistry(registry_name="model")

example_record = model_registry.list_cards(name="linnerrud", as_dataframe=False)[0]

model_card = model_registry.load_card(uid=example_record.get("uid"))
print(model_card.version)
# > 1.0.0
model_registry.register_card()
