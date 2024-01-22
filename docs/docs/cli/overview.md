# Command Line Interface for Opsml Server

Out of the box, `Opsml` comes pre-installed with a [`Opsml-Cli`](https://github.com/shipt/opsml-cli), which is a Rust-compiled binary that can be used as a CLI to interact with an `Opsml` server. CLI commands are listed below. 

## Listing Cards

command: `list-cards`


```bash
opsml-cli list-cards --registry "model" --name "linnerud" --repository "opsml" --limit 10
```

Will list available cards in a registry

### Args

- **registry**: Card registry to search
- **name**: Name of card
- **repository**: Repository associated with card
- **version**: Version of card
- **uid**: Uid of card
- **max-date**: Max date to search. Must be in `YYYY-MM-DD` format
- **limit**: Max number of records to return
- **tag_name**: Tag name to search
- **tag_value**: Tag value to search

### Download Model Metadata and Model

commands: `download-model-metadata`, `download-model`

```bash
# download model metadata
opsml-cli download-model-metadata --name "linnerud" --repository "opsml" --version "1.0.0"

# download model (this will also download metadata)
opsml-cli download-model --uid {{model_uid}}
```

Will download model metadata or model from a registry

### Args

- **name**: Name of card
- **repository**: Repository associated with card
- **version**: Version of card
- **uid**: Uid of card
- **write-dir**: Directory to write to

### Get Model Metrics

command: `get-model-metrics`

```bash
opsml-cli get-model-metrics --name "linnerud" --repository "opsml" --version "1.0.0"
```

Prints metrics associated with a ModelCard

- **name**: Name of card
- **repository**: repository associated with card
- **version**: Version of card
- **uid**: uid of card

### Compare Model Metrics

command: `compare-model-metrics`

```bash
opsml-cli compare-model-metrics --challenge-uid {{challenger_uid}} --champion-uid {{champion_uid}} --metric-name "accuracy" --lower-is-better false
```

Runs a comparison between a model challenger and *n* model champions

- **challenger_uid**: UID of challenger model
- **champion_uid**: Champion UIDs
- **metric_name**: Metrics to compare
- **lower_is_better**: Whether a lower metric is better

