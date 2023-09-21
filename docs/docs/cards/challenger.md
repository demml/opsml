# Challenger

One of the benefits to linking and tracking `ModelCards` along with various `Runcard` metrics is that it's relatively easy to compare different model versions via the `ModelChallenger` class.

## Examples

- [Comparing registered models](#comparing-registered-models)
- [Comparing new un-registered model with registered models](#comparing-new-model-prior-to-registration)

## Comparing registered models

The following example will create 3 different model versions across 3 different runs. The `ModelChallenger` will then be used to compare the models.

All code blocks can be run as one script. We will break them up to explain what's going on.

### **Import**

```python

#sklearn
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, PoissonRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, ModelCard
from opsml.projects import ProjectInfo, MlflowProject
from opsml.model.challenger import ModelChallenger
```

### **Create Example Data**

It is recommended to also create data within a `Run`; however, for this example it's not needed.

```python

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Split indices
indices = np.arange(data.shape[0])

# usual train-val split
train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")

# Create card
datacard = DataCard(
    info=card_info,
    data=data,
    dependent_vars=["Pulse"],
    data_splits=[
        DataSplit(label="train", indices=train_idx),
        DataSplit(label="test", indices=test_idx),
    ],
)
data_reg = CardRegistry(registry_name="data")
data_reg.register_card(card=datacard)

```

### **Create First Model**

We will now train a linear regression model and score it with the test dataset

```python

info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
project = MlflowProject(info=info)
with project.run(run_name="challenger-lin-reg") as run:
    datacard = data_reg.load_card(uid=datacard.uid)
    splits = datacard.split_data()

    reg = LinearRegression()
    reg.fit(splits.train.X.to_numpy(), splits.train.y)

    reg_preds = reg.predict(splits.test.X.to_numpy())
    mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
    run.log_metric("mae", value=mae)

    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=splits.train.X[0:1],
        name="linear_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=datacard.uid,
        tags={"example": "challenger"},
    )
    run.register_card(card=model_card)

```

### **Create Second Model**

Train a Lasso regression model

```python

info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
project = MlflowProject(info=info)
with project.run(run_name="challenger-lasso") as run:
    datacard = data_reg.load_card(uid=datacard.uid)
    splits = datacard.split_data()

    reg = Lasso()
    reg.fit(splits.train.X.to_numpy(), splits.train.y)

    reg_preds = reg.predict(splits.test.X.to_numpy())
    mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
    run.log_metric("mae", value=mae)

    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=splits.train.X[0:1],
        name="lasso_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=datacard.uid,
        tags={"example": "challenger"},
    )
    run.register_card(card=model_card)

```


### **Create Third Model**

Train a Poisson regression model

```python

info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
project = MlflowProject(info=info)
with project.run(run_name="challenger-poisson") as run:
    datacard = data_reg.load_card(uid=datacard.uid)
    splits = datacard.split_data()

    reg = PoissonRegressor()
    reg.fit(splits.train.X.to_numpy(), splits.train.y)

    reg_preds = reg.predict(splits.test.X.to_numpy())
    mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
    run.log_metric("mae", value=mae)

    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=splits.train.X[0:1],
        name="poisson_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=datacard.uid,
        tags={"example": "challenger"},
    )
    run.register_card(card=model_card)

```

### **Run ModelChallenger**

We will now run comparison for all model via the `ModelChallenger` class. To create a challenger battle report, you will first need to identify the model that will be the `Challenger` when instantiating `ModelChallenger`. In this example we with use **linear_reg** as our challenger.

```python

# lets first load the linear_reg model
model_registry = CardRegistry(registry_name="model")
linreg_card = model_registry.load_card(
    name="linear_reg",
    team="mlops",
    tags={"example": "challenger"},
)

# Instantiate the challenger class and pass the linear_reg card as the challenger
challenger = ModelChallenger(challenger=linreg_card)

# Challenge 1 or more champion models based on the `mae` metric that was record for all models
reports = challenger.challenge_champion(
    metric_name="mae",
    lower_is_better=True,
    champions=[
        CardInfo(name="lasso_reg", team="mlops", version="1.0.0"),
        CardInfo(name="poisson_reg", team="mlops", version="1.0.0"),
    ],
)

# can also access the battle report objects directly
print([report.model_dump() for report in reports["mae"]])
```

```json
[
    {
        "champion_name": "lasso_reg",
        "champion_version": "1.0.0",
        "champion_metric": {
            "name": "mae",
            "value": 13.986761128923671,
            "step": None,
            "timestamp": None,
        },
        "challenger_metric": {
            "name": "mae",
            "value": 14.923992178323557,
            "step": None,
            "timestamp": None,
        },
        "challenger_win": False,
    },
    {
        "champion_name": "poisson_reg",
        "champion_version": "1.0.0",
        "champion_metric": {
            "name": "mae",
            "value": 13.471315607483495,
            "step": None,
            "timestamp": None,
        },
        "challenger_metric": {
            "name": "mae",
            "value": 14.923992178323557,
            "step": None,
            "timestamp": None,
        },
        "challenger_win": False,
    },
]
```

## Comparing new model prior to registration

The following example will train a model, create a card (without registering it), and then compare it to a registered model. This is useful for when you want to compare a challenger or candidate model to already registered models.

### **Create Champion Model**

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import numpy as np

from opsml.projects import ProjectInfo

from opsml.projects.mlflow import MlflowProject
from opsml.registry import DataCard, ModelCard
from opsml.model.challenger import ModelChallenger


def fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    X["col_11"] = np.random.randint(1, 20, size=(1000, 1))

    y = np.random.randint(1, 10, size=(1000, 1))
    return X, y


info = ProjectInfo(
    name="opsml",
    team="devops",
    user_email="test_email",
)
project = MlflowProject(info=info)
with project.run(run_name="create-model") as run:
    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)
    mae = mean_absolute_error(y, reg.predict(X))
    data_card = DataCard(
        data=X,
        name="pipeline-data1",
        team="mlops-test",
        user_email="mlops.com",
    )
    data_card.create_data_profile()

    run.register_card(card=data_card)

    # register champion model - needed for example
    champion_model = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name=f"linear-reg",
        team="mlops-test",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        tags={"name": "model_tag"},
    )
    run.log_metric("mae", mae)
```
### **Create and Compare Challenger Model**

Here we will create a run, train a new model, instantiate a `ModelCard` for the challenger and then compare it to the champion model prior to registration.

```python
info = ProjectInfo(
    name="opsml",
    team="devops",
    user_email="test_email",
)
project = MlflowProject(info=info)
with project.run(run_name="challenge-model") as run:
    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)
    mae = mean_absolute_error(y, reg.predict(X))

    # create challenger model card
    challenger_model = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name=f"linear-reg",
        team="mlops-test",
        user_email="mlops.com",
    )

    challenger = ModelChallenger(challenger=challenger_model)

    # challenge previous champion before registering challenger
    # this will pull the previous model version
    report = challenger.challenge_champion(
        metric_name="mae",
        metric_value=mae,  # could be metric from training
        lower_is_better=True,
    )

    if report["mae"][0].challenger_win:
        # now we register cards
        data_card = DataCard(
            data=X,
            name="pipeline-data1",
            team="mlops-test",
            user_email="mlops.com",
        )
        run.register_card(card=data_card)

        # append uid
        challenger_model.datacard_uid = data_card.uid
        run.register_card(card=challenger_model)
```

### Docs

::: opsml.model.challenger.ModelChallenger
    options:
        members:
            - __init__
            - challenge_champion
        show_root_heading: true
        show_source: true
        heading_level: 3