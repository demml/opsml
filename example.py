import os
import pandas as pd

# os.environ["OPSML_TRACKING_URI"] = "http://0.0.0.0:8000"
# os.environ["OPSML_TRACKING_URI"] = "https://opsml-api.ml.us-central1.staging.shipt.com/"

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

print(f"OPSML_TRACKING_URI: {os.environ['OPSML_TRACKING_URI']}")

from sklearn.linear_model import LinearRegression
import numpy as np

from opsml.projects import ProjectInfo
from opsml.projects import OpsmlProject

from opsml.registry.cards import ModelCardMetadata, Description, DataCardMetadata, DataSplit
from opsml.registry import DataCard, ModelCard, CardRegistries

registries = CardRegistries()


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
    name="test-project",
    team="devops-ml",
    user_email="test_email",
)
project = OpsmlProject(info=info)

with project.run() as run:
    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)
    data_card = DataCard(
        data=X,
        name="pandas-data",
        team="devops-ml",
        user_email="mlops.com",
        data_splits=[
            DataSplit(label="train", column_name="col_1", column_value=0.5),
            DataSplit(label="test", column_name="col_1", column_value=0.5),
        ],
        sql_logic={
            "table1": "select * from table1",
            "table2": "select * from table2",
        },
        metadata=DataCardMetadata(
            feature_descriptions={"col_1": "this is a feature"},
        ),
        dependent_vars=["col_1"],
    )

    data_card.create_data_profile()
    run.register_card(card=data_card)

    # datacard: DataCard = registries.data.load_card(uid=data_card.uid)

    # register 1st model - this is arbitrary
    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name=f"linear-reg-model",
        team=f"devops-ml",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        tags={"name": "model_tag"},
        metadata=ModelCardMetadata(
            description=Description(
                summary="model_readme.md",
            )
        ),
    )
    run.register_card(card=model_card)

    # fake metric
    run.log_metric("mape", 5)
    run.log_metric("mae", 5)
    run.log_metric("mae2", 5)
    for i in range(0, 10):
        run.log_metric(f"mae{i}", 5)
    run.log_parameter("param1", 5)
    run.log_artifact("test1", "hello, world")
    # run.log_artifact_from_file("tests/assets/cats.jpg", "misc")
