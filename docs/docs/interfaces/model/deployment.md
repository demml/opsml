# Deployment

While `Opsml` is not an all-in-one platform that will deploy your model in one click (maybe one day :smile:), it does provide a helper class and a happy path to deploy your model. This is outlined below.

```mermaid
flowchart LR
    subgraph Client
    user(fa:fa-user DS) -->|create| data(fa:fa-table Data)
    data -->|create|model(fa:fa-brain Model)
    data -->|package in|datacard(DataCard)
    model -->|package in|modelcard(ModelCard)
    datacard -->|associate|modelcard
    end 

    subgraph Server
    datacard -->|insert into|datareg[(DataRegistry)]
    modelcard -->|insert into|modelreg[(ModelRegistry)]
    end

    subgraph CICD
    modelreg --> dir(Direcotry)
    dir --> |package|docker(DockerFile)
    end


    subgraph API
    loaded(ModelLoader) -->|load|loaded_model(Model)
    end

    docker --> API

    subgraph UI
    vis(visualize)
    end

    user --> vis
    modelreg -->|view in|UI
    datareg -->|view in|UI


    style Client rx:10,ry:10
    style Server rx:10,ry:10
    style CICD rx:10,ry:10
    style API rx:10,ry:10
    style UI rx:10,ry:10


    style user fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style data fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style model fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style datacard fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style modelcard fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style loaded fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style dir fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style docker fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style loaded_model fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style vis fill:#028e6b,stroke:black,stroke-width:2px,color:white,font-weight:bolder

    style datareg fill:#5e0fb7,stroke:black,stroke-width:2px,color:white,font-weight:bolder
    style modelreg fill:#5e0fb7,stroke:black,stroke-width:2px,color:white,font-weight:bolderack
```

## Steps:

### DS Worflow

1. DS creates data and model
2. DS packages data and model into appropriate interfaces and `DataCard` and `ModelCard`, respectively.
3. `DataCard` and `ModelCard` are registered and pushed to their respective registries.

### CICD Workflow

1. During CICD, the model is downloaded from the `ModelRegistry` via the `Opsml CLI` to a directory
2. Model directory and API logic are packaged into a docker image

### API Workflow

1. Docker image is deployed to a server.
2. During startup, the API logic leverages the `ModelLoader` class to load the model from the directory.
3. Model is now ready to be used by the API.

::: opsml.model.ModelLoader
    options:
        show_root_heading: true
        show_source: true
        heading_level: 4