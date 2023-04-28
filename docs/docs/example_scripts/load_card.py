from opsml.registry import CardRegistry

model_regitstry = CardRegistry(registry_name="model")

example_record = model_regitstry.list_cards(name="linnerrud", as_dataframe=False)[0]

model_card = model_regitstry.load_card(uid=example_record.get("uid"))
print(model_card.version)
# > 1.0.0
