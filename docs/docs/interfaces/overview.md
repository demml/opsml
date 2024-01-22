# Overview

<p align="center">
  <img src="../../images/opsml-interfaces.png" width="577"/>
</p>


Interfaces are one of the 3 primary objects in `Opsml` and can be viewed as a low-level object with the most flexibility. Although each subclassed interface is unique, they are all designed to be injected into a `ModelCard` or `DataCard`

## Interface Types

- [`DataInterface`](./data/interfaces.md): Interface used to store data-related information (data, dependent variables, feature descriptions, split logic, etc.)

- [`ModelInterface`](./model/interfaces.md): Interface used to store trained model and model information

## Data Interface

The `DataInterface` is the primary interface for working with data in `Opsml`. It is designed to be subclassed and can be used to store data in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `PandasData`: Stores data from a pandas dataframe
- `NumpyData`: Stores data from a numpy array
- `PolarsData`: Stores data from a polars dataframe
- `ArrowData`: Stores data from a pyarrow table
- `ImageDataset`: Stores data from a directory of images
- `TextDataset`: Stores data from a directory of text files
- `TorchtData`: Stores data from a torch tensor(s)
- `SqlData`: Stores sql text

## Model Interface

The `ModelInterface` is the primary interface for working with models in `Opsml`. It is designed to be subclassed and can be used to store models in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `SklearnModel`: Stores data from a sklearn model
- `TorchModel`: Stores data from a pytorch model
- `LightningModel`: Stores data from a pytorch lightning model
- `HuggingFaceModel`: Stores data from a huggingface model
- `TensorFlowModel`: Stores data from a tensorflow model
- `XGBoostModel`: Stores data from a xgboost model
- `LightGBMModel`: Stores data from a lightgbm model
- `CatBoostModel`: Stores data from a catboost model


For more information on interfaces, see the each interface's respective documentation.
