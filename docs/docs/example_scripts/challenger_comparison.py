import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889/"

# typing
from typing import Optional

# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_absolute_error
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, ModelCard
from opsml.projects import ProjectInfo, MlflowProject

"""
The following will create 2 separate runs. Ideally you could also break this up so that you only 
Create the data once and create models on 2 distinct runs
"""

info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
project = MlflowProject(info=info)


def lin_reg_run():
    with project.run(run_name="challenger-lin-reg") as run:
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
        run.register_card(card=datacard)
        splits = datacard.split_data()

        reg = LinearRegression().fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=data[0:1],
            name="linear_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=datacard.uid,
        )
        run.register_card(card=model_card)


def lasso_run():
    with project.run(run_name="challenger-lin-reg") as run:
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
        run.register_card(card=datacard)
        splits = datacard.split_data()

        reg = Lasso().fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=data[0:1],
            name="lasso_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=datacard.uid,
        )
        run.register_card(card=model_card)
