# Versioning

All cards follow a semver version format (`major.minor.patch`). By default, a `minor` increment is used whenever a card is registered. If a version is provided, it overrides the default version type.

For more information on the versioning scheme, please refer to the [Semver](https://semver.org/) documentation. In addition, opsml leverage the [semver](https://docs.rs/semver/1.0.26/semver/) crate to ensure semver compliance.

Card versions can also be assigned pre and build tags.

- Pre tag for a release candidate -> `major.minor.patch-rc.{#}` -> `1.0.0-rc.1` -> version_type: "pre"

- Build tag -> `major.minor.patch+build.{#}` -> `1.0.0+build.1` -> version_type: "build"

Allowed types of versioning:

- `major`: Major version increment
- `minor`: Minor version increment (default)
- `patch`: Patch version increment
- `pre`: Pre-release version increment
- `build`: Build version increment
- `pre_build`: Pre-release and build version increment

```python
from opsml import CardRegistry, VersionType

registry = CardRegistry("model")

# skipping logic

# major
registry.register_card(card=card, version_type=VersionType.Major)
# minor
registry.register_card(card=card, version_type=VersionType.Minor)
# patch
registry.register_card(card=card, version_type=VersionType.Patch)
# pre
registry.register_card(card=card, version_type=VersionType.Pre)
# build
registry.register_card(card=card, version_type=VersionType.Build)
# pre_build
registry.register_card(card=card, version_type=VersionType.PreBuild)
```

???note "Recommended Usage"
    The ability to provide a `version` is only an option to enable flexibility; it is not required. The recommended approach if you don't need release candidates or extra flexibility is to create a `Card` and specify the `version_type` when registering a card, which will allow `OpsML` to handle the versioning for you. 

## What happens when I register a card?

When you register a card, opsml will search for the most recent version of the card, and depending on the version types and any pre and/or build tags you provide, it will increment the version accordingly.

```python
card = ModelCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type=VersionType.Pre, pre_tag="foo")
# 1.0.0-foo
```

In a normal workflow (like on model retraining), it's recommended to let opsml use it's defaults to increment the version.

```python
# model training
registry.register_card(card=card)
# 1.0.0

# model retraining
registry.register_card(card=card)
# 1.1.0

# model retraining
registry.register_card(card=card)
# 1.2.0
```

## Terminology:

### `Major`
Indicates a breaking change

- **Examples**:
    * Adding new features to a dataset
    * New model architecture
    * Training same model architecture but with additional features (major change for both data and model)

### `Minor`
Non-breaking changes that typically add functionality

- **Examples**:
    * Updating data/sql logic
    * Updating model parameters
    * Features and output remain the same

### `Patch`
Indicates a non-breaking change

- **Examples**:
    * model re-training
    * data re-freshes

### `Pre`
Indicates a release candidate

- **Examples**:
    * Saved model that is not ready for an official release
    * Candidate data that needs to be further validated

### `Build`
Indicates a build tag

- **Examples**:
    * Appending git commit hash to a version

These are all general guidelines and we recommend to use what works best for your team. For example, if you team prefers not to mess around with versioning, you may wish to default every model re-training to a `minor` version. 