if __name__ == "__main__":
    # create_fake_data requires polars and pandas to be installed
    from opsml.helpers.data import create_fake_data
    from opsml import SklearnModel, CardRegistry, TaskType, ModelCard, RegistryType
    from sklearn import ensemble  # type: ignore

    # start registries
    reg = CardRegistry(RegistryType.Model)  #

    # create data
    X, y = create_fake_data(n_samples=1200)

    # Create and train model
    classifier = ensemble.RandomForestClassifier(n_estimators=5)
    classifier.fit(X.to_numpy(), y.to_numpy().ravel())

    model_interface = SklearnModel(  #
        model=classifier,
        sample_data=X[0:10],
        task_type=TaskType.Classification,
    )
    model_interface.create_drift_profile(alias="drift", data=X)  #

    modelcard = ModelCard(  #
        interface=model_interface,
        space="opsml",
        name="my_model",
    )

    # register model
    reg.register_card(modelcard)

    # This code will run as is
