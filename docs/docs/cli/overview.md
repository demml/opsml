# Command Line Interface for Opsml Server

`Opsml` also includes a few helper CLI commands that work directly with a server.


## `download-model` and `download-model-metadata` Args

Will download a model and/or it's metadata to a local folder

`name`
: Name of model

`team`
: Team associated with model

`version`
: Version of model

`uid`
: uid of model

`write-dir`
: Folder to download model object to


## `list_cards` Args

Will list available models in a registry

`registry`
: Card registry to search

`name`
: Name of card

`team`
: Team associated with card

`version`
: Version of card

`uid`
: uid of card

## Docs

::: opsml.cli.api_cli
    options:
        members:
            - download_model
            - download_model_metadata
            - list_cards
        show_root_heading: true
        show_source: true
        heading_level: 3