from opsml.projects import ProjectInfo, MlflowProject


def _test_example(mlflow_project: MlflowProject):
    ########### Challenger example

    from sklearn.datasets import load_linnerud
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression, Lasso, PoissonRegressor
    from sklearn.metrics import mean_absolute_error
    import numpy as np

    # Opsml
    from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, ModelCard
    from opsml.projects import ProjectInfo, MlflowProject
    from opsml.model.challenger import ModelChallenger

    ### **Create Example Data**

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

    info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
    project = MlflowProject(info=info)
    with mlflow_project.run(run_name="challenger-lin-reg") as run:
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

    info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
    project = MlflowProject(info=info)
    with mlflow_project.run(run_name="challenger-lasso") as run:
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

    info = ProjectInfo(name="opsml", team="devops", user_email="test_email")
    project = MlflowProject(info=info)
    with mlflow_project.run(run_name="challenger-poisson") as run:
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

    model_registry = CardRegistry(registry_name="model")
    linreg_card = model_registry.load_card(
        name="linear_reg",
        team="mlops",
        tags={"example": "challenger"},
    )

    challenger = ModelChallenger(challenger=linreg_card)

    reports = challenger.challenge_champion(
        metric_name="mae",
        lower_is_better=True,
        champions=[
            CardInfo(name="lasso_reg", team="mlops", version="1.0.0"),
            CardInfo(name="poisson_reg", team="mlops", version="1.0.0"),
        ],
    )

    print([report.dict() for report in reports["mae"]])


def test_datacard(db_registries):
    from sklearn.datasets import load_linnerud
    from sklearn.model_selection import train_test_split
    import numpy as np

    # Opsml
    from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit

    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    # Split indices
    indices = np.arange(data.shape[0])

    # usual train-val split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
    data_card = DataCard(
        info=card_info,
        data=data,
        dependent_vars=["Pulse"],
        # define splits
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )

    # splits look good
    splits = data_card.split_data()
    print(splits.train.X.head())

    data_registry = db_registries["data"]
    data_registry.register_card(card=data_card)
    print(data_card.version)
    # > 1.0.0

    # list cards
    cards = data_registry.list_cards(
        uid=data_card.uid,
        as_dataframe=False,
    )  # can also supply, name, team, version
    print(cards[0])


def test_data_splits():
    import polars as pl
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    df = pl.DataFrame(
        {
            "foo": [1, 2, 3, 4, 5, 6],
            "bar": ["a", "b", "c", "d", "e", "f"],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )

    datacard = DataCard(
        info=info,
        data=df,
        data_splits=[
            DataSplit(label="train", column_name="foo", column_value=6, inequality="<"),
            DataSplit(label="test", column_name="foo", column_value=6),
        ],
    )

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 5
    assert splits.test.X.shape[0] == 1

    import numpy as np
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    data = np.random.rand(10, 10)

    datacard = DataCard(info=info, data=data, data_splits=[DataSplit(label="train", indices=[0, 1, 5])])

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 3

    #### **Start and Stop Slicing**

    import numpy as np
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    data = np.random.rand(10, 10)

    datacard = DataCard(info=info, data=data, data_splits=[DataSplit(label="train", start=0, stop=3)])

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 3
