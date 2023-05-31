# Versioning

All `ArtifactCards` follow a Semver version format (major.minor.path). By default, a `minor` increment is used whenver a card is registered. 

```python
registry.register_card(card=card, version_type="patch") # patch increment 1.0.0 -> 1.0.1
registry.register_card(card=card, version_type="minor") # minor increment (default) 1.0.0 -> 1.1.0
registry.register_card(card=card, version_type="major") # major increment 1.0.0 -> 2.0.0
```

### Terminology:

`patch`
: Usually indicates a bug fix with backwards compatability

`minor`
: Indicates additional funcitonality or updates that preserve backwards compatability

- **Examples**:
    * data refresh
    * model re-training

`major`
: Indicates changes that break backwards compatibility

- **Examples**:

    * Adding new features to a dataset
    * New model architecture
    * Training same model architecture but with additional features (major change for both data and model)
