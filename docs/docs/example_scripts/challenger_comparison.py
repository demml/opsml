import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8888/"

# typing
from typing import Optional

# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso, PoissonRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, ModelCard
from opsml.projects import ProjectInfo, MlflowProject
from opsml.model.challenger import ModelChallenger

###################### Create data
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


###################### Create 1st model
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


###################### Create 2nd model
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


###################### Create 3rd model
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


######################### Challenger

model_registry = CardRegistry(registry_name="model")
linreg_card = model_registry.load_card(
    name="linear_reg",
    team="mlops",
    tags={"example": "challenger"},
)

challenger = ModelChallenger(challenger=linreg_card)
reports = challenger.challenge_champion(
    metric_name="mae",
    champions=[
        CardInfo(name="lasso_reg", team="mlops", version="1.0.0"),
        CardInfo(name="poisson_reg", team="mlops", version="1.0.0"),
    ],
    lower_is_better=True,
)

# can also access the battle report objects directly
print([report.dict() for report in reports])
# [
#    {
#        "champion_name": "lasso_reg",
#        "champion_version": "1.0.0",
#        "champion_metric": {"name": "mae", "value": 10.753896568020215, "step": None, "timestamp": None},
#        "challenger_metric": {"name": "mae", "value": 5.778116866806702, "step": None, "timestamp": None},
#        "challenger_win": True,
#    },
#    {
#        "champion_name": "poisson_reg",
#        "champion_version": "1.0.0",
#        "champion_metric": {"name": "mae", "value": 6.2403608293470345, "step": None, "timestamp": None},
#        "challenger_metric": {"name": "mae", "value": 5.778116866806702, "step": None, "timestamp": None},
#        "challenger_win": True,
#    },
# ]
