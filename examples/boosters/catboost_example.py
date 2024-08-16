# pylint: disable=invalid-name

import catboost

from opsml import (
    CardInfo,
    CardRegistries,
    CatBoostModel,
    DataCard,
    DataSplit,
    ModelCard,
    PolarsData,
)
from opsml.helpers.data import create_fake_data


class OpsmlCatBoostWorkflow:
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
        X, y = create_fake_data(n_samples=1000, task_type="classification", to_polars=True)
        X = X.with_columns((y).to_series().alias("target"))

        # Create data interface
        data_interface = PolarsData(
            data=X,
            data_splits=[
                DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
                DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
            ],
            dependent_vars=["target"],
        )

        # Create datacard
        datacard = DataCard(interface=data_interface, info=self.info)
        self.registries.data.register_card(card=datacard)

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the CatBoostModel.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

        # load data from server
        datacard.load_data()

        # split data
        data = datacard.split_data()

        # fit model
        clf = catboost.CatBoostClassifier()
        clf.fit(data["train"].X.to_numpy(), data["train"].y.to_numpy())

        # create model interface
        interface = CatBoostModel(model=clf, sample_data=data["train"].X.to_numpy())

        # create modelcard
        modelcard = ModelCard(
            interface=interface,
            info=self.info,
            to_onnx=True,  # lets convert onnx
            datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
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

        # load onnx model
        modelcard.load_onnx_model()

        inputs = data["test"].X.to_numpy()[:2].astype("float32")

        print(modelcard.onnx_model.sess.run(None, {"features": inputs}))

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="catboost", repository="opsml", contact="user@email.com")
    workflow = OpsmlCatBoostWorkflow(info=info)
    workflow.run_workflow()
