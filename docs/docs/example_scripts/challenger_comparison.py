import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889/"

# typing
from typing import Optional

# Data
from sklearn.datasets import load_linnerud
from sklearn.model_selection import train_test_split
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, Modelcard
from opsml.projects import ProjectInfo, MlflowProject


def create_data_card() -> str:
    """Creates a datacard used by both models"""

    info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
    project = MlflowProject(info=info)

    with project.run(run_name="challenger-comparison") as run:
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
            # define splits
            data_splits=[
                DataSplit(label="train", indices=train_idx),
                DataSplit(label="test", indices=test_idx),
            ],
        )
        run.register_card(card=datacard)
        run.add_tag("id", "challenger-comparison")

    return run.info.run_id


def create_first_model_card() -> str:
    """Creates first model card"""

    run_registry = CardRegistry(registry_name="run")
    run = run_registry.list_cards(name="opsml", team="devops", tags={"id": "challenger-comparison"}, as_dataframe=False)

    info = ProjectInfo(
        name="opsml",
        team="devops",
        user_email="test_email",
        run_id=run[0]["uid"],
    )
    project = MlflowProject(info=info)

    with project.run(run_name="challenger-comparison") as run:
        data_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
        datacard = run.load_card(registry_name="data", info=data_info)
