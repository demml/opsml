# Versioning

All `ArtifactCards` follow a Semver version format (`major.minor.patch`). By default, a `minor` increment is used whenever a card is registered. If a version is provided, it overrides the default version type.

Cards can also be versioned as a release candidate and/or attached with a build tag (you can use default or provide your own tags when registering a card).
- Release candidate -> `major.minor.patch-rc.{#}` -> `1.0.0-rc.1` -> version_type: "pre"
- Build tag -> `major.minor.patch+build.{#}` -> `1.0.0+build.1` -> version_type: "build"
- Release candidate with build tag -> `major.minor.patch-rc.{#}+build.{#}` -> `1.0.0-rc.1+build.1` -> version_type: "pre_build"

## Recommended Flow
- The ability to provide `version` is only an option to enable flexibility; it is not required. The recommended approach if you don't need release candidates or extra flexibility is to create a `Card` and specify the `version_type` when registering a card, which will allow `OpsML` to handle the versioning for you. 

```python
modelcard = ModelCard(
    name="model", 
    team="opsml", 
    sample_input_data=data, 
    trained_model=model,
    datacard_uid=datacard.uid,
    )

model_registry.register_card(
    card=modelcard, 
    version_type="patch",
    )
# let OpsML take care of figuring out the version
```

## Rules for release candidates and build tags:
1. A full `major.minor.patch` version must be specified in the card.
2. `version_type` must be either `pre`, `build` or `pre_build`.
3. Supply custom tags to either `pre_tag` or `build_tag` if you prefer to override defaults.
4. `build-tags` are allowed to be attached to "official" `major.minor.patch` versions. Thus, it's possible to have `1.0.0` and `1.0.0+build.1` as valid versions in the registry. In this scenario `1.0.0+build.1` would be given precedence when listing or loading a card.

```python
card = ModelCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="pre", pre_tag="foo")
# 1.0.0-foo.1
```

5. Registering a card with the same information (above) will increment the pre-release and/or build tag.
6. Incrementing a pre-release tag resets the build tag counter.
7. If a card is registered with a `major`, `minor` or `patch` increment **and** there are only pre-release or build candidates associated with the respective `major.minor.patch` the version will be incremented to the corresponding `valid` version.

```python

# 1st rc
card = DataCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="pre")
# 1.0.0-rc.1

#2nd rc
card = DataCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="pre")
# 1.0.0-rc.2


#Official
card = DataCard(**kwargs)
registry.register_card(card=card)
# 1.0.0
```

All Cards accept manual insertion of `major.minor.patch`, `major.minor` or `major`. If a version is supplied, `opsml` will search the associated registry for the latest version that matches the supplied version. As an example, if the latest registered version of a card is `1.2.0` and a new card is registered with a version specified as `1.2` and a `version_type` of `patch`, `opsml` will increment the version to `1.2.1`.

Example:
```python

card = DataCard(**kwargs)
registry.register_card(card=card)
# 1.2.0

card = DataCard(**kwargs, version="1.2")
registry.register_card(card=card, version_type="patch")
# 1.2.1
```

### Other Examples:

```python

# Major, Minor and Patch
registry.register_card(card=card, version_type="patch") # patch increment 1.0.0 -> 1.0.1
registry.register_card(card=card, version_type="minor") # minor increment (default) 1.0.0 -> 1.1.0
registry.register_card(card=card, version_type="major") # major increment 1.0.0 -> 2.0.0

# Pre, Build, Pre_Build
card = DataCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="pre") # pre-release or release candidate increment -> 1.0.0-rc.1


card = DataCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="build") # build increment -> 1.0.0+build.1


card = DataCard(**kwargs, version="1.0.0")
registry.register_card(card=card, version_type="pre_build") # pre-release and build increment -> 1.0.0-rc.1+build.1


# Create a minor increment and associate it with a build tag (git commit hash)
card = DataCard(**kwargs)
registry.register_card(card=card, build_tag="git.1a5d783h3784") # minor increment with build tag -> 1.1.0+git.1a5d783h3784
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
## `Build`
Indicates a build tag

- Associated metadata tags
---