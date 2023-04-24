Cards (aka Artifact Cards) are one of the primary interfaces for working with `Opsml`.

<p align="center">
  <img src="../../images/card-flow.png" width="457" height="332"/>
</p>

## Card Types

- `DataCard`: Card used to store data-related information (data, dependent variables, feature descriptions, split logic, etc.)
- `ModelCard`: Card used to store trained model and model information
- `RunCard`: Stores artifact and metric info related to Data, Model, or Pipeline cards.
- `PipelineCard`: Stores information related to a training pipeline and all other cards created within the pipeline (Data, Run, Model)
- `ProjectCard`: Stores information related to unique projects. You will most likely never interact with this card directly.
