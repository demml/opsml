# Command Line Interface for Opsml Server

`Opsml` also includes a few helper CLI commands that work directly with a server.


### `download-model` and `download-model-metadata`

Will download a model and/or it's metadata to a local folder

- **name**: Name of model
- **team**: Team associated with model
- **version**: Version of model
- **uid**: uid of model
- **write-dir**: Folder to download model object to


### `list-cards`

Will list available models in a registry

- **registry**: Card registry to search
- **name**: Name of card
- **team**: Team associated with card
- **version**: Version of card
- **uid**: uid of card
- **max-date**: Max date to search. Must be in `YYYY-MM-DD` format
- **limit**: Max number of records to return

### `get-model-metrics`

Prints metrics associated with a ModelCard

- **name**: Name of card
- **team**: Team associated with card
- **version**: Version of card
- **uid**: uid of card

### `download-data-profile`

Downloads a data profile from a DataCard

- **name**: Name of card
- **team**: Team associated with card
- **version**: Version of card
- **uid**: uid of card

### `compare-data-profiles`

Takes a list of version or uids and runs data profile comparisons

- **name**: Name of card
- **team**: Team associated with card
- **version**: List of versions to compare
- **uid**: List of uids to compare

#### Docs

::: opsml.cli.api_cli
    options:
        members:
            - download_model
            - download_model_metadata
            - list_cards
            - get_model_metrics
            - download_data_profile
            - compare_data_profiles
        show_root_heading: true
        show_source: true
        heading_level: 3