# Challenger

One of the benefits to linking and tracking `ModelCards` along with various `Runcard` metrics is that it's relatively easy to compare different model versions via the `ModelChallenger` class.

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
print([report.dict() for report in reports["mae"]])
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

### Docs

::: opsml.model.challenger.ModelChallenger
    options:
        members:
            - __init__
            - challenge_champion
        show_root_heading: true
        show_source: true
        heading_level: 3