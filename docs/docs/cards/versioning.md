# Versioning

All `ArtifactCard`s follow a Semver version format (major.minor.path). By default, a `minor` increment is used whenver a card is registered. 

```python
registry.register_card(card=card, version_type="patch") # patch increment 1.0.0 -> 1.0.1
registry.register_card(card=card, version_type="minor") # minor increment (default) 1.0.0 -> 1.1.0
registry.register_card(card=card, version_type="major") # major increment 1.0.0 -> 2.0.0
```

### Terminology:

---
## `Major`
Indicates a breaking change

- **Examples**:
    * Adding new features to a dataset
    * New model architecture
    * Training same model architecture but with additional features (major change for both data and model)

---
## `Minor`
Non-breaking changes that typically add functionality

- **Examples**:
    * Updating data/sql logic
    * Updating model parameters
    * Features and output remain the same

---
## `patch`
Indicates a non-breaking change

- **Examples**:
    * model re-training
    * data re-freshes

---
## `pre`
Indicates a release candidate

- **Examples**:
    * Saved model that is not ready for an official release
    * Candidate data that needs to be further validated
---