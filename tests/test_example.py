def test_example1(setup_database):

    # import
    from opsml_data import DataCard, DataRegistry
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split

    # registry
    # registry = DataRegistry()
    registry: DataRegistry = setup_database

    # create fake data
    mu_1, mu_2 = -4, 4
    X_data = np.random.normal(mu_1, 2.0, size=(1000, 10))
    y_data = np.random.randint(2, 100, size=(1000, 1))

    col_names = []
    for i in range(0, X_data.shape[1]):
        col_names.append(f"col_{i}")

    # Create dataframe
    data = pd.DataFrame(X_data, columns=col_names)
    data["target"] = y_data
    data.head()

    # train test split
    train_idx, test_idx = train_test_split(np.arange(data.shape[0]), test_size=0.3)

    # Data card
    DATA_NAME = "synthetic_data"
    TEAM = "SPMS"
    USER_EMAIL = "steven.forrester@shipt.com"
    DATA_SPLITS = [{"label": "train", "indices": train_idx}, {"label": "test", "indices": test_idx}]

    data_card = DataCard(
        data_name=DATA_NAME,
        team=TEAM,
        user_email=USER_EMAIL,
        data=data,
        data_splits=DATA_SPLITS,
    )

    # split
    splits = data_card.split_data()

    # save to registry
    registry.register_data(data_card=data_card)

    # list data
    registry_data = registry.list_data(data_name=DATA_NAME, team=TEAM)
    assert data_card.uid == registry_data["uid"].values[0]

    # load data_card
    new_data_card = registry.load_data(data_name=DATA_NAME, team=TEAM)
    assert new_data_card.uid == data_card.uid


def test_example2(setup_database):

    # import
    from opsml_data import DataCard, DataRegistry, DriftDetector, DriftVisualizer
    import numpy as np
    import pandas as pd

    # registry
    # registry = DataRegistry()
    registry: DataRegistry = setup_database

    # create fake data
    mu_1 = -4  # mean of the first distribution
    mu_2 = 4  # mean of the second distribution
    X_train = np.random.normal(mu_1, 2.0, size=(1000, 10))
    cat = np.random.randint(0, 3, 1000).reshape(-1, 1)
    X_train = np.hstack((X_train, cat))

    X_test = np.random.normal(mu_2, 2.0, size=(1000, 10))
    cat = np.random.randint(2, 5, 1000).reshape(-1, 1)
    X_test = np.hstack((X_test, cat))

    y_train = np.random.randint(1, 100, size=(1000, 1))
    y_test = np.random.randint(2, 100, size=(1000, 1))

    col_names = []
    for i in range(0, X_train.shape[1]):
        col_names.append(f"col_{i}")

    X_train = pd.DataFrame(X_train, columns=col_names)
    X_test = pd.DataFrame(X_test, columns=col_names)

    # run drift report
    drift_detector = DriftDetector(
        x_reference=X_train,
        x_current=X_test,
        y_reference=y_train,
        y_current=y_test,
        target_feature_name="target",
        categorical_features=["col_10"],
    )

    # run drift diagnos
    drift_report = drift_detector.run_drift_diagnostics()

    # add data to dataframe
    X_train["target"] = y_train
    X_test["target"] = y_test
    X_train["split"] = "train"
    X_test["split"] = "test"
    model_data = pd.concat([X_train, X_test])

    # Data card
    DATA_NAME = "synthetic_data"
    TEAM = "SPMS"
    USER_EMAIL = "steven.forrester@shipt.com"

    # notice that column split is specified differently this time
    DATA_SPLITS = [
        {"label": "train", "column": "split", "column_value": "train"},
        {"label": "train", "column": "split", "column_value": "test"},
    ]

    data_card = DataCard(
        data_name=DATA_NAME,
        team=TEAM,
        user_email=USER_EMAIL,
        data=model_data,
        data_splits=DATA_SPLITS,
        dependent_vars=["target"],
        drift_report=drift_report,
    )
    registry.register_data(data_card=data_card)

    # reload data card and visualize drift report
    loaded_data_card = registry.load_data(data_name=DATA_NAME, team=TEAM, version=data_card.version)
    DriftVisualizer(drift_report=loaded_data_card.drift_report).visualize_report()


def test_example3(setup_database):
    # import
    from opsml_data import DataCard, DataRegistry, DriftDetector, DriftVisualizer, SnowflakeQueryRunner
    import numpy as np
    import pandas as pd

    # registry
    # registry = DataRegistry()
    registry: DataRegistry = setup_database
    runner = SnowflakeQueryRunner(on_vpn=True)
    df = runner.query_to_dataframe(sql_file="data.sql")
    features = [
        "NBR_ADDRESSES",
        "NBR_ORDERS",
        "NBR_RX",
        "NBR_APT",
        "METRO_X",
        "METRO_Y",
        "METRO_Z",
        "APT_FLG",
        "DROP_OFF_TIME",
    ]
    DEPENDENT_VAR = "DROP_OFF_TIME"

    # Data card
    DATA_NAME = "tarp_drop_off"
    TEAM = "SPMS"
    USER_EMAIL = "steven.forrester@shipt.com"
    DATA_SPLITS = [
        {"label": "train", "column": "EVAL_FLG", "column_value": 0},
        {"label": "test", "column": "EVAL_FLG", "column_value": 1},
    ]

    data_card = DataCard(
        data=df,
        data_name=DATA_NAME,
        team=TEAM,
        user_email=USER_EMAIL,
        data_splits=DATA_SPLITS,
        dependent_vars=[DEPENDENT_VAR],
    )

    splits = data_card.split_data()

    detector = DriftDetector(
        x_reference=splits.train[features],
        y_reference=splits.train[DEPENDENT_VAR].to_numpy().reshape(-1, 1),
        x_current=splits.test[features],
        y_current=splits.test[DEPENDENT_VAR].to_numpy().reshape(-1, 1),
        target_feature_name=DEPENDENT_VAR,
        categorical_features=["APT_FLG"],
    )

    chart = detector.visualize_report()
    data_card.drift_report = detector.run_drift_diagnostics()
    registry.register_data(data_card=data_card)
    registry_data = registry.list_data(data_name=DATA_NAME, team=TEAM, version=data_card.version)
    assert registry_data["drift_uri"].values[0] is not None
