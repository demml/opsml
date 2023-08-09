# Versioning

All `ArtifactCard`s follow a Semver version format (major.minor.patch). By default, a `minor` increment is used whenever a card is registered. If a version is provided, it overrides the default version type.

Cards can also be versioned as a release candidate with the format `major.minor.patch-rc.#` (e.g. "1.0.0-rc.2). To create a release candidate, the version must be manually specified before registering the card.

All Cards also accept manual insertion of `major.minor.patch`, `major.minor` or `major`. If a version is supplied, `opsml` will search the associated registry for the latest version that matches the supplied version. As an example, if the latest registered version of a card is `1.2.0` and a new card is registered with a version specified as `1.2` and a `version_type` or `patch`, `opsml` will increment the version to `1.2.1`.

```python
registry.register_card(card=card, version_type="patch") # patch increment 1.0.0 -> 1.0.1
registry.register_card(card=card, version_type="minor") # minor increment (default) 1.0.0 -> 1.1.0
registry.register_card(card=card, version_type="major") # major increment 1.0.0 -> 2.0.0

# pre release example
card.version = "1.2.0-rc.1"
registry.register_card(card=card)

# major.minor example
card.version = "1.2"
registry.register_card(card=card, version_type="patch")
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
## `Patch`
Indicates a non-breaking change

- **Examples**:
    * model re-training
    * data re-freshes

---
## `Pre`
Indicates a release candidate

- **Examples**:
    * Saved model that is not ready for an official release
    * Candidate data that needs to be further validated
---