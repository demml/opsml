import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error

from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import CardInfo, DataCard, ModelCard

card_info = CardInfo(name="linear-reg", team="opsml", user_email="user@email.com")

# to use runs, you must create and use a project
project_info = ProjectInfo(name="opsml-dev", team="opsml", user_email="user@email.com")
project = OpsmlProject(info=project_info)


def create_fake_data():
    X_train = np.random.normal(-4, 2.0, size=(1000, 10))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X = pd.DataFrame(X_train, columns=col_names)
    y = np.random.randint(1, 10, size=(1000, 1))

    return X, y


# start the run
with project.run(run_name="optional_run_name") as run:

    X, y = create_fake_data()

    # train model
    lasso = Lasso(alpha=0.5)
    lasso = lasso.fit(X.to_numpy(), y)

    preds = lasso.predict(X.to_numpy())

    mape = mean_absolute_percentage_error(y, preds)

    # Create metrics / params
    run.log_metric(key="mape", value=mape)
    run.log_param(key="alpha", value=0.5)

    # lets use card_info instead of writing required args multiple times
    data_card = DataCard(data=X, info=card_info)
    run.register_card(card=data_card, version_type="major")  # you can specify "major", "minor", "patch"

    model_card = ModelCard(
        trained_model=lasso,
        sample_input_data=X,
        datacard_uid=data_card.uid,
        info=card_info,
    )
    run.register_card(card=model_card)

print(run.runcard.get_metric("mape"))
# > Metric(name='mape', value=0.8489706297619047, step=None, timestamp=None)

print(run.runcard.get_param("alpha"))
# > Param(name='alpha', value=0.5)
