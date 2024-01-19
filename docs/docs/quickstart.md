To get a quick feel for `Opsml`, run the following code in a new terminal. The following uses Mlflow as a UI interface and local storage and sqlite.

### Start Local Server

<div class="termy">

```console
$ opsml-uvicorn-server

...
<span style="color: green;">INFO</span>:     [INFO] Started server process
<span style="color: green;">INFO</span>:     [INFO] Waiting for application startup

...
<span style="color: green;">INFO</span>:     [INFO] Application startup complete
<span style="color: green;">INFO</span>:     [INFO] Uvicorn running on http://0.0.0.0:8888
```

</div>

Next, open a new terminal and run the following python script. Make sure to set the `OPSML_TRACKING_URI` which tells `opsml` where to log experiments.


## Run Initial Python Script

```bash
export OPSML_TRACKING_URI=${YOUR_TRACKING_URI}
```

```python
# imports
from sklearn.linear_model import LinearRegression
from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    ModelCard,
    PandasData,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data


info = CardInfo(name="linear-regression", repository="opsml", user_email="user@email.com")
registries = CardRegistries()


#--------- Create DataCard ---------#

# create fake data
X, y = create_fake_data(n_samples=1000, task_type="regression")
X["target"] = y

# Create data interface
data_interface = PandasData(
    data=X,
    data_splits=[
        DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
        DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
    ],
    dependent_vars=["target"],
)

# Create and register datacard
datacard = DataCard(interface=data_interface, info=info)
registries.data.register_card(card=datacard)

#--------- Create ModelCard ---------#

# split data
data = datacard.split_data()

# fit model
reg = LinearRegression()
reg.fit(data.train.X.to_numpy(), data.train.y.to_numpy())

# create model interface
interface = SklearnModel(
    model=reg,
    sample_data=data.train.X.to_numpy(),
    task_type="regression",  # optional
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True,  # lets convert onnx
    datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
)
registries.model.register_card(card=modelcard)
```


## Opsml UI

Next, navigate to `OPSML_TRACKING_URI` and you should see the following:


<p align="left">
  <img src="../images/quickstart-list.png"  width="450" height="230"/>
</p>

Click on the `linear-regression` card and you should see the following:

<p align="left">
  <img src="../images/quickstart-model.png"  width="651" height="410"/>
</p>

Click on the `DataCard` button and you should see the following:

<p align="left">
  <img src="../images/quickstart-data.png"  width="559" height="410"/>
</p>

## Download your model via CLI

Try downloading your model via the CLI:

```bash
opsml-cli download-model --name 'linear-regression' --version '1.0.0'
```
Here we are downloading the model with name `linear-regression` and version `1.0.0`. You could also provide the `uid` of the model instead of the name and version. By default, the cli command will download objects to the `models` directory. You will see both the model `joblib` file as well as the model's associated `metadata`. If you'd wish to download the `onnx` version of the model, you can add the `--onnx` flag to the command.

```bash
opsml-cli download-model --name 'linear-regression' --version '1.0.0' --onnx
```