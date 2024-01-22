from tests.conftest import cleanup


def test_quickstart():

    from sklearn.linear_model import LinearRegression

    from opsml import (
        CardInfo,
        CardRegistries,
        DataCard,
        DataSplit,
        ModelCard,
        PandasData,
        SklearnModel,
    )
    from opsml.helpers.data import create_fake_data

    info = CardInfo(name="linear-regression", repository="opsml", user_email="user@email.com")
    registries = CardRegistries()

    # create fake data
    X, y = create_fake_data(n_samples=1000, task_type="regression")
    X["target"] = y

    # Create data interface
    data_interface = PandasData(
        data=X,
        data_splits=[
            DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
            DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
        ],
        dependent_vars=["target"],
    )

    # Create and register datacard
    datacard = DataCard(interface=data_interface, info=info)
    registries.data.register_card(card=datacard)

    # --------- Create ModelCard ---------#

    # split data
    data = datacard.split_data()

    # fit model
    reg = LinearRegression()
    reg.fit(data.train.X.to_numpy(), data.train.y.to_numpy())

    # create model interface
    interface = SklearnModel(
        model=reg,
        sample_data=data.train.X.to_numpy(),
        task_type="regression",  # optional
    )

    # create modelcard
    modelcard = ModelCard(
        interface=interface,
        info=info,
        to_onnx=True,  # lets convert onnx
        datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
    )
    registries.model.register_card(card=modelcard)

    cleanup()
