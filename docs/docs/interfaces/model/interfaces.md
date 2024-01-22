# Model Interface

The `ModelInterface` is the primary interface for working with models in `Opsml`. It is designed to be subclassed and can be used to store models in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `SklearnModel`: Stores data from a sklearn model
- `TorchModel`: Stores data from a pytorch model
- `LightningModel`: Stores data from a pytorch lightning model
- `HuggingFaceModel`: Stores data from a huggingface model
- `TensorFlowModel`: Stores data from a tensorflow model
- `XGBoostModel`: Stores data from a xgboost model
- `LightGBMModel`: Stores data from a lightgbm model
- `CatBoostModel`: Stores data from a catboost model

### Required Arguments

`model`
: Model to save. See subclasses for supported model types

`sample_data`
: Sample of data that is fed to the model at inference time. As an example, if you are using a `SklearnModel` you would provide a numpy array at prediction time, so `sample_data` should be a numpy array for X features.

### Optional Arguments

`onnx_model`
: `OnnxModel` object. This is typically auto-generated when creating a `ModelCard` with `to_onnx=True`. You can also BYO `OnnxModel` object. See [OnnxModel](./onnx.md) for more information.

`task_type`
: Task type of the model. This is mainly used for `HuggingFaceModel`, but can be supplied for any model interface if the user chooses.


---
## SklearnModel

Interface for saving an Sklearn model

|  |  |
| --- | --- |
| **Model Type** | `sklearn.base.BaseEstimator` |
| **Save Format** | `joblib` |
| **Source** | [`SklearnModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/sklearn.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/sklearn/basic.py) |



### Arguments

`model`: `BaseEstimator`
: Sklearn model

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[pd.DataFrame, NDArray[Any]]`
: Sample data to be used for model inference.
For sklearn models this should be a pandas DataFrame or numpy array.
This should match exactly what the model expects as input.


### Example

```py hl_lines="1  14"
from opsml import SklearnModel, CardInfo, ModelCard, CardRegistry
from sklearn.linear_model import LinearRegression

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

reg = LinearRegression()
reg.fit(X_train, y_train)

# create model interface
interface = SklearnModel(model=reg,sample_data=X_train)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True,  # lets convert onnx
    datacard_uid=datacard.uid,
)

model_registry.register_card(card=modelcard)
```

---
## LightGBMModel

Interface for saving a LightGBM booster or sklearn flavor model

|  |  |
| --- | --- |
| **Model Type** | `Booster` or `LGBMModel` |
| **Save Format** | `text` or `joblib` |
| **Source** | [`LightGBMModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/lgbm.py) |
| **Example 1** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/boosters/lightgbm_boost.py) |
| **Example 2** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/boosters/lightgbm_sklearn.py) |


### Arguments

`model`: `Union[Booster, LGBMModel]`
: LightGBM booster or Sklearn flavor model

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[pd.DataFrame, NDArray[Any]]`
: Sample data to be used for model inference.

### Example

```py hl_lines="1  22"
from opsml import LightGBMModel, CardInfo, ModelCard, CardRegistry
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

scaler = StandardScaler()
X_train = scaler.transform(X)
X_test = scaler.transform(X)

lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# train model
gbm = lgb.train(params, lgb_train, ...)

# fit model
interface = LightGBMModel(model=gbm, sample_data=X_train[:100], preprocessor=scaler)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True,
    datacard_uid=datacard.uid,
)
model_registry.register_card(card=modelcard)
```

---
## XGBoostModel

Interface for saving a XGBoost model. Only sklearn flavor is currently supported. `XGBoostModel` is a subclass of `SklearnModel`.

|  |  |
| --- | --- |
| **Model Type** | `XGBModel` |
| **Save Format** | `joblib` |
| **Source** | [`XGBoostModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/xgb.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/boosters/xgboost_sklearn.py) |


### Arguments

`model`: `XGBModel`
: XGBoost model

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[pd.DataFrame, NDArray[Any]]`
: Sample data to be used for model inference.
For xgboost models this should be a pandas DataFrame or numpy array.
This should match exactly what the model expects as input. See example below.

### Example

```py hl_lines="1  14"
from opsml import XGBoostModel, CardInfo, ModelCard, CardRegistry
import xgboost as xgb

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

reg = xgb.XGBRegressor(n_estimators=3, max_depth=3)
reg.fit(X_train, y_train)

# create model interface
interface = XGBoostModel(model=reg, sample_data=data.train.X.to_numpy()[:, 0:5])

# create modelcard
modelcard = ModelCard(info=info, interface=interface, datacard_uid=datacard.uid)

# register
model_registry.register_card(card=modelcard)

```

---
## CatBoostModel

Interface for saving a CatBoost model.

|  |  |
| --- | --- |
| **Model Type** | `CatBoost` |
| **Save Format** | `cbm` |
| **Source** | [`CatBoostModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/catboost_.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/boosters/catboost_example.py) |


### Arguments

`model`: `CatBoost`
: CatBoost Regressor, Classifier or Ranker

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[List[Any], NDArray[Any]]`
: Sample data to be used for model inference.
For catboost models this is either a list or numpy array.

### Example

```py hl_lines="1  14"
from opsml import CatBoostModel, CardInfo, ModelCard, CardRegistry
import catboost

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

clf = catboost.CatBoostClassifier()
clf.fit(X_train, y_train)

# create model interface
interface = CatBoostModel(model=clf, sample_data=X_train)

# create modelcard
modelcard = ModelCard(info=info, interface=interface, datacard_uid=datacard.uid)

# register
model_registry.register_card(card=modelcard)
```

---
## TorchModel

Interface for saving a PyTorch model.

|  |  |
| --- | --- |
| **Model Type** | `torch.nn.Module` |
| **Save Format** | `torch` |
| **Source** | [`TorchModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/pytorch.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/torch/torch_example.py) |


### Arguments

`model`: `torch.nn.Module`
: A pytorch model that subclasses `torch.nn.Module`

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[torch.Tensor, Dict[str, torch.Tensor], List[torch.Tensor], Tuple[torch.Tensor]]`
: Sample data to be used for model inference.

`save_args`: `Optional[TorchSaveArgs]
: Optional arguments for saving the model. See [TorchSaveArgs](./extras.md#torchsaveargs) for more information.

`onnx_args`: `Optional[TorchOnnxArgs]`
: Optional arguments for converting to onnx. See [TorchOnnxArgs](./onnx.md#torchonnxargs) for more information.

### Note On Saving and Loading

If you wish to save the model's state dict, as is recommended by pytorch, you will need to specify `save_args=TorchSaveArgs(as_state_dict=True)` or
`save_args{"as_state_dict": True}` to the `TorchModel` interface. This will save the model's learned parameters ONLY. If you wish to load the state dict back into the model during loading, you can supply an optional `model_arch` named attr to `load_model` that will be used to load the state dict (`load_model(model_arch=model)`). If you do not supply a `model_arch` only the state dict will be loaded into the model. If you do not specify `save_args`, pytorch will attempt to save the model architecture which may raise a `local object pickle error`.


### Example

```py hl_lines="1  15-19 34"
from opsml import TorchModel, CardInfo, ModelCard, CardRegistry
from examples.torch.polynomial_nn import Polynomial3 # see examples/torch/polynomial_nn.py

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

# instantiate model
model = Polynomial3()
model.train_model(X, y)

# torch interface
interface = TorchModel(
    model=model, 
    sample_data=X, 
    save_args= TorchSaveArgs(as_state_dict=True),
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True, 
    datacard_uid=datacard.uid,  
)

# register
model_registry.register_card(card=modelcard)

# load card
modelcard = model_registry.load_card()
modelcard.load_model(model_arch=model)
```

---
## LightningModel

Interface for saving a PyTorch Lightning model.

|  |  |
| --- | --- |
| **Model Type** | `Trainer` |
| **Save Format** | `ckpt` |
| **Source** | [`LightningModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/pytorch_lightning.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/torch/torch_lightning_example.py) |


### Arguments

`model`: `Trainer`
: A pytorch lightning `Trainer` object

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[torch.Tensor, Dict[str, torch.Tensor], List[torch.Tensor], Tuple[torch.Tensor]]`
: Sample data to be used for model inference.

`onnx_args`: `Optional[TorchOnnxArgs]`
: Optional arguments for converting to onnx. See [TorchOnnxArgs](./onnx.md#torchonnxargs) for more information.

### Note on Saving and Loading

During saving, `LightningModel` will extract the model from the trainer and save a checkpoint. Upon loading, you can supply an optional `model_arch` argument to `load_model` (e.g. `load_model(model_arch=model)`) to load the model from a checkpoint. If no model architecture is provided, the checkpoint will be loaded from the path object via `torch.load`.

### Example

```py hl_lines="1  18-26 41"
from opsml import LightningModel, TorchOnnxArgs, CardInfo, ModelCard, CardRegistry
from examples.torch.lightning_module import RegressionModel # see examples/torch/
import lightning as L

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

# fit model
model = RegressionModel()
trainer = L.Trainer(max_epochs=10)
trainer.fit(model)


# lightning interface
interface = LightningModel(
    model=trainer,
    sample_data=X,
    onnx_args=TorchOnnxArgs(
        input_names=["predict"],
        output_names=["output"],
        dynamic_axes={"predict": {0: "batch_size"}},  # allow for >=1 batch size
    ),
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True, 
    datacard_uid=datacard.uid,  
)

# register
model_registry.register_card(card=modelcard)

# load
modelcard = model_registry.load_card()
modelcard.load_model(model_arch=model)
```

---
## TensorFlowModel

Interface for saving a tensorflow model.

|  |  |
| --- | --- |
| **Model Type** | `tf.keras.Model` |
| **Save Format** | `tensorflow` |
| **Source** | [`TensorFlowModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/tf.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/tensorflow/tf_example.py) |


### Arguments

`model`: `tf.keras.Model`
: A tensorflow model that subclasses `tf.keras.Model`

`preprocessor`: `Optional[Any]`
: Optional preprocessor

`sample_data`: `Union[ArrayType, Dict[str, ArrayType], List[ArrayType], Tuple[ArrayType]]` (ArrayType= `Union[NDArray[Any], tf.Tensor]`)
: Sample data to be used for model inference.

### Example

```py hl_lines="1  22"
from opsml import TensorFlowModel, CardInfo, ModelCard, CardRegistry
import tensorflow as tf 

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

# build and compile model
model = tf.keras.Sequential(
    [
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(1),
    ]
)
model.compile(loss="mean_absolute_error", optimizer=tf.keras.optimizers.Adam(0.001))
model.fit(X, y, epochs=10)

# tensorflow interface
interface = TensorFlowModel(model=model, sample_data=X)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True, 
    datacard_uid=datacard.uid,  
)

# register
model_registry.register_card(card=modelcard)
```

---
## HuggingFaceModel

Interface for saving a huggingface model.

|  |  |
| --- | --- |
| **Model Type** | `Union[Pipeline, PreTrainedModel, TFPreTrainedModel]` |
| **Save Format** | `huggingface` |
| **Source** | [`HuggingFaceModel`](https://github.com/shipt/opsml/blob/main/opsml/model/interfaces/huggingface.py) |
| **Example** | [`Link`](https://github.com/shipt/opsml/blob/main/examples/huggingface/hf_example.py) |


### Arguments

`model`: `Union[Pipeline, PreTrainedModel, TFPreTrainedModel]`
: A huggingface model that subclasses `Pipeline`, `PreTrainedModel` or `TFPreTrainedModel`

`tokenizer`: `Optional[Union[PreTrainedTokenizer, PreTrainedTokenizerFast]]`
: Optional huggingface tokenizer

`feature_extractor`: `Optional[Union[FeatureExtractionMixin, ImageProcessingMixin]]`
: Optional huggingface feature extractor

`sample_data`: `Union[list, tuple, dict, BatchEncoding, BatchFeature, str, ImageFile]`
: Sample data to be used for model inference.

`onnx_args`: `Optional[HuggingFaceOnnxArgs]`
: Optional arguments for converting to onnx. See [HuggingFaceOnnxArgs](./onnx.md#huggingfaceonnxargs) for more information.

`task_type`: `str`
: Model task. Must be task from `HuggingFaceTask`. See [HuggingFaceTask](./extras.md#huggingfacetask) for more information.

### Example

```py hl_lines="1  15-23"
from opsml import HuggingFaceModel, HuggingFaceOnnxArgs, HuggingFaceORTModel, HuggingFaceTask, CardInfo, ModelCard, CardRegistry
from transformers import BartModel, BartTokenizer

info = CardInfo(name="model", repository="opsml", contact="user@email.com")
model_registry = CardRegistry("model")

# Skipping data step
...

tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
model = BartModel.from_pretrained("facebook/bart-base")
inputs = tokenizer(["Hello. How are you"], return_tensors="pt")

# huggingface interface
model = HuggingFaceModel(
    model=model,
    tokenizer=tokenizer,
    sample_data=inputs,
    task_type=HuggingFaceTask.FEATURE_EXTRACTION.value,
    onnx_args=HuggingFaceOnnxArgs(
        ort_type=HuggingFaceORTModel.ORT_FEATURE_EXTRACTION.value,
    ),
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True, 
    datacard_uid=datacard.uid,  
)

# register
model_registry.register_card(card=modelcard)
```