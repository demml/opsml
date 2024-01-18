from metaflow import FlowSpec, step
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


class OpsmlFlow(FlowSpec):
    """
    Metaflow example using Opsml

    Steps:
        - Get data and create datacard with pandas interface
        - Create linear regressor model and create modelcard with sklearn interface
        - Load modelcard and test onnx predictions
    """

    info = CardInfo(name="metaflow_example", repository="opsml", contact="user@email.com")

    @step
    def start(self):
        """Create datacard"""
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

        # Create datacard
        datacard = DataCard(interface=data_interface, info=self.info)
        registries.data.register_card(card=datacard)
        self.datacard_uid = datacard.uid

        self.next(self.create_modelcard)

    @step
    def create_modelcard(self):
        """Create modelcard"""
        registries = CardRegistries()

        datacard: DataCard = registries.data.load_card(uid=self.datacard_uid)

        # load data from server
        datacard.load_data()

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
            info=self.info,
            to_onnx=True,  # lets convert onnx
            datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
        )

        registries.model.register_card(card=modelcard)
        self.modelcard_uid = modelcard.uid
        self.next(self.end)

    @step
    def end(self):
        """Test onnx model from modelcard"""
        registries = CardRegistries()
        datacard: DataCard = registries.data.load_card(uid=self.datacard_uid)
        modelcard: ModelCard = registries.model.load_card(uid=self.modelcard_uid)

        # load data for testing
        datacard.load_data()

        # split data
        data = datacard.split_data()

        # load model
        modelcard.load_model()

        # load onnx model
        modelcard.load_onnx_model()

        prediction = modelcard.onnx_model.sess.run(None, {"predict": data.test.X.to_numpy()[:5].astype("float32")})
        print(prediction)


if __name__ == "__main__":
    OpsmlFlow()
