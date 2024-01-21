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
from opsml.types import Description, ModelCardMetadata


class OpsmlWorkflow:
    def __init__(self, info: CardInfo):
        """Instantiates workflow class. Instantiation will also set up the registries that
        will be used to store cards and artifacts

        Args:
            info:
                CardInfo data structure that contains required info for cards.
                You could also provide "name", "repository" and "email" to a card; however, this
                simplifies the process.

        """
        self.info = info
        self.registries = CardRegistries()

    def _create_datacard(self):
        """Shows how to create a data interface and datacard

        You can think of cards as outputs to each step in your workflow.
        In your data getting step, you will get your data, create a data interface,
        and then create/register a datacard, which will be stored in the registry.

        This example highlights the uses of the PandasData interface
        """

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

        # Create data profile
        data_interface.create_data_profile()

        # Create datacard
        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the SklearnModel interface and how you can load
        and split data from a datacard.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

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
            metadata=ModelCardMetadata(
                description=Description(summary="card_summary.md"),  # add markdown summary
            ),
        )
        self.registries.model.register_card(card=modelcard)

    def _test_onnx_model(self):
        """This shows how to load a modelcard and the associated model and onnx model (if converted to onnx)"""

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        modelcard: ModelCard = self.registries.model.load_card(name=self.info.name)

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

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="linear-regression", repository="opsml", contact="user@email.com")

    workflow = OpsmlWorkflow(info=info)
    workflow.run_workflow()
