import os
import pandas as pd
import matplotlib.pyplot as plt

# os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889"

from sklearn.linear_model import LinearRegression
import numpy as np

from opsml.projects import ProjectInfo, OpsmlProject
from opsml.registry import DataCard, ModelCard


def fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    y = np.random.randint(1, 10, size=(1000, 1))
    return X, y


info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
project = OpsmlProject(info=info)

with project.run(run_name="test-run") as run:
    X, y = fake_data()
    reg = LinearRegression().fit(X.to_numpy(), y)

    data_card = DataCard(
        data=X,
        name="pipeline-data",
        team="mlops",
        user_email="mlops.com",
    )

    run.register_card(card=data_card)

    # create a fake figure
    fig, ax = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis
    ax.plot([0, 1, 2], [10, 20, 3])
    array = np.random.random((10, 10))
    fig.savefig("test.png")  # save the figure to file
    plt.close(fig)
    run.log_artifact_from_file(local_path="test.png")

    model_card = ModelCard(
        trained_model=reg,
        sample_input_data=X[0:1],
        name="linear_reg",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
    )
    run.register_card(card=model_card)
    for i in range(0, 100):
        run.log_metric("test", i)

    run.log_parameter("blaaaaaah", 10)
