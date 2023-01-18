<h1 align="center">
  <br>
  <img src="images/opsml-artifacts-logo-cropped.png"  width="409" height="123" alt="py opsml logo"/>
  <br>
</h1>

<h4 align="center">Trading cards for machine learning workflows.</h4>

<p align="center">
  <a href="https://drone.shipt.com/shipt/py-opsml">
  <img alt="Build Status" src="https://drone.shipt.com/api/badges/shipt/opsml-data/status.svg"/>

  <a href="https://www.python.org/downloads/release/python-390/">
  <img alt="Python" src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Blue_Python_3.9_Shield_Badge.svg" />

  <img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="quality gate" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=alert_status&token=squ_06f8921843044242e5975ed012023f7b09066e9c" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="coverage" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=coverage&token=squ_06f8921843044242e5975ed012023f7b09066e9c" />
</p>

<p align="center">
  <a href="#what-is-it">What is it?</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#create-a-card">Create a Card</a> •
  <a href="#datacard">DataCard</a> •
  <a href="#modelcard">ModelCard</a> 
</p>

## What is it?

`OpsML-Artifacts` is a library for tracking,  storing, versioning, and reproducing artifacts (aka Artifact Cards) across the ML-lifecycle. Think of it as trading cards for machine learning.

<p align="center">
  <img src="images/card-flow.png"  width="480" height="400" alt="py opsml logo"/>
</p>

## Features:
  - **Simple Design**:  Standardized design for all card types and registries to make switching between and registering different cards easy.

  - **Automation**: Automatic type checking (the power of pydantic!) for card attributes. Automated processes depending on card type (Onnx conversion for model, api signature generation, data schema creation)

  - **Short**: Easy to integrate into your existing workflows. You just need a card type and a registry to get started

## Installation:
Before installing, you will need to set up your Artifactory credentials.

#### Request credentials for [Artifactory](https://techhub.shipt.com/engineering/infrastructure/devops/artifactory/) in Slack `#ask-info-sec`

Once you have your credentials, set the following variables.
```bash
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_USERNAME=your_username
export POETRY_HTTP_BASIC_SHIPT_RESOLVE_PASSWORD=your_password
```

If using poetry, you must also add the following in your `pyproject.toml`
```toml
[[tool.poetry.source]]
name = "shipt-resolve"
url = "https://artifactory.shipt.com/artifactory/api/pypi/pypi-virtual/simple"
default = true
```

Next, add opsml-artifacts to your environment
```bash
poetry add opsml-artifacts
```

### GCP Resources
`OpsML-Artifacts` relies on GCP resources for managing Artifact Cards. As a result you will need to configure your GCP credentials (easy to do) in 1 of 2 ways.

1. Set `GOOGLE_ACCOUNT_JSON_BASE64` as an env variable. This key can be found in our slack channel.

```bash
export GOOGLE_ACCOUNT_JSON_BASE64='our shared key'
```

2. Install the [google cloud sdk](https://cloud.google.com/sdk/docs/install) and make sure you are added to our core gcp project (tbd)

## Create a Card

Think of ArtifactCards as trading cards that you can link together in a set or deck. Each card can exist independently and provides descriptive information related to the card type.

There are 4 card types in `Opsml-Artifacts`.

Card Types:
- `DataCard`: Card used to store data-related information (data, dependent variables, feature descriptions, split logic, etc.)
- `ModelCards`: Card used to store trained model and model information
- `ExperimentCard`: Stores artifact and metric info related to Data, Model, or Pipeline cards.
- `PipelineCard`: Stores information related to training pipeline and all other cards created within the pipeline (Data, Experiment, Model)

Quit the yapping and show me an example!

## DataCard
The following example shows how to create a DataCard. For more information on what you can do with DataCards, refer to additional examples in the example dir.

```python
from opsml_artifacts import SnowflakeQueryRunner, DataCard, CardRegistry

query_runner = SnowflakeQueryRunner(on_vpn=True) #query runner is a temporary wrapper for pyshipt sql (needed for network issues in vertex, see opsml-pipelines docs)

dataframe = query_runner.query_to_dataframe(sql_file="data.sql") #executes sql file or raw sql. data.sql is in examples dir

# Subset features
features = [
    "NBR_ADDRESSES",
    "NBR_ORDERS",
    "NBR_RX",
    "NBR_APT",
    "METRO_X",
    "METRO_Y",
    "METRO_Z",
    "APT_FLG",
    "DROP_OFF_TIME",
    "EVAL_FLG",
]
DEPENDENT_VAR = "DROP_OFF_TIME"

# Define DataCard attributes (see examples dir for more detailed information)
DATA_NAME = "tarp_drop_off"
TEAM = "SPMS"
USER_EMAIL = "steven.forrester@shipt.com"
DATA_SPLITS = [
    {"label": "train", "column": "EVAL_FLG", "column_value": 0},
    {"label": "test", "column": "EVAL_FLG", "column_value": 1},
]

# Create DataCard
data_card = DataCard(
    data=dataframe[features],
    name=DATA_NAME,
    team=TEAM,
    user_email=USER_EMAIL,
    data_splits=DATA_SPLITS,
    dependent_vars=[DEPENDENT_VAR],
)

#register card
data_registry = CardRegistry(registry_name="data") # CardRegistry accepts "data", "model", "pipeline" and "experiment"
data_registry.register_card(card=data_card)
```

#### Output
```text
{"level": "INFO", "message": "Table: tarp_drop_off registered as version 1", "timestamp": "2023-01-18T16:47:04.772149Z", "app_env": "development", "host": null, "version": null}
```

### Searching for and Loading Existing DataCards
```python
from opsml_artifacts import CardRegistry

data_registry = CardRegistry(registry_name="data")
tarp_list = data_registry.list_cards(team="SPMS", name="tarp_drop_off")

print(tarp_list.loc[:, ~tarp_list.columns.isin(["feature_map", "data_splits", "drift_uri"])].to_markdown()) # Filter some of the columns for readability
```
#### Output
|    | uid                              | date       |     timestamp | app_env   | name          | team   |   version | user_email                 | data_uri                                                                                                        | feature_descriptions   | data_type   | dependent_vars    |
|---:|:---------------------------------|:-----------|--------------:|:----------|:--------------|:-------|----------:|:---------------------------|:----------------------------------------------------------------------------------------------------------------|:-----------------------|:------------|:------------------|
|  0 | 9e03984187034382b3ee74d30519f4eb | 2023-01-18 | 1674059839649 | staging   | tarp_drop_off | SPMS   |         2 | steven.forrester@shipt.com | gs://shipt-spms-stg-bucket/DATA_REGISTRTY/SPMS/tarp_drop_off/version-2/1a7d7f2d1e4749f692654bced16b7d5b.parquet |                        | DataFrame   | ['DROP_OFF_TIME'] |
|  1 | 0c551c4dbfe9478ab3094def3b5b2e5d | 2023-01-18 | 1674059839649 | staging   | tarp_drop_off | SPMS   |         1 | steven.forrester@shipt.com | gs://shipt-spms-stg-bucket/DATA_REGISTRTY/SPMS/tarp_drop_off/version-1/a51f81f7b64d4cf791a3585264ba18c9.parquet |                        | DataFrame   | ['DROP_OFF_TIME'] |

```python

loaded_card = data_registry.load_card(uid="9e03984187034382b3ee74d30519f4eb") # load_card can take a few arguments. Be sure to check the docstring
print(loaded_card.data.head().to_markdown())
```

#### Output
|    |   NBR_ADDRESSES |   NBR_ORDERS |   NBR_RX |   NBR_APT |   METRO_X |   METRO_Y |   METRO_Z |   APT_FLG |   DROP_OFF_TIME |   EVAL_FLG |
|---:|----------------:|-------------:|---------:|----------:|----------:|----------:|----------:|----------:|----------------:|-----------:|
|  0 |              11 |           11 |        0 |        11 | -1990.75  |  -4926.25 |   3515.48 |         1 |        34.4031  |          1 |
|  1 |               2 |            2 |        0 |         2 | -1990.75  |  -4926.25 |   3515.48 |         1 |         4.54011 |          1 |
|  2 |               4 |            4 |        0 |         4 |  1233.15  |  -4782.66 |   4024.31 |         1 |         9.23536 |          1 |
|  3 |              11 |           12 |        0 |        12 |   971.158 |  -5637.71 |   2804.05 |         1 |        59.68    |          1 |
|  4 |               3 |            3 |        0 |         3 |   746.07  |  -5612.94 |   2920.26 |         1 |         5.38533 |          1 |