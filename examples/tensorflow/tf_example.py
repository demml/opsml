import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras

from opsml import CardInfo, CardRegistries, DataCard, DataSplit, ModelCard, PandasData
from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.tf import TensorFlowModel

logger = ArtifactLogger.get_logger()


class OpsmlTensorFlowWorkflow:
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

    def create_datacard(self):
        """Shows how to create a data interface and datacard

        You can think of cards as outputs to each step in your workflow.
        In your data getting step, you will get your data, create a data interface,
        and then create/register a datacard, which will be stored in the registry.

        This example highlights the uses of the PandasData interface
        """
        logger.info("Creating datacard")

        # create fake data
        url = "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
        column_names = [
            "MPG",
            "Cylinders",
            "Displacement",
            "Horsepower",
            "Weight",
            "Acceleration",
            "Model Year",
            "Origin",
        ]

        dataset = pd.read_csv(url, names=column_names, na_values="?", comment="\t", sep=" ", skipinitialspace=True)
        dataset = dataset.dropna()
        dataset["Origin"] = dataset["Origin"].map({1: "USA", 2: "Europe", 3: "Japan"})
        dataset = pd.get_dummies(dataset, columns=["Origin"], prefix="", prefix_sep="")

        # Create datacard
        idx = np.arange(dataset.shape[0])
        train_idx, test_idx = train_test_split(idx, test_size=0.2)

        data_interface = PandasData(
            data=dataset,
            data_splits=[
                DataSplit(label="train", indices=list(train_idx)),
                DataSplit(label="val", indices=list(test_idx)),
            ],
            dependent_vars=["MPG"],
        )

        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _build_and_compile_model(self) -> tf.keras.Model:
        model = keras.Sequential(
            [
                keras.layers.Dense(64, activation="relu"),
                keras.layers.Dense(64, activation="relu"),
                keras.layers.Dense(1),
            ]
        )

        model.compile(loss="mean_absolute_error", optimizer=tf.keras.optimizers.Adam(0.001))
        return model

    def create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the TensorFlowModel interface.
        """
        logger.info("Creating modelcard")

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

        # load data from server
        datacard.load_data()
        splits = datacard.split_data()

        model = self._build_and_compile_model()
        model.fit(
            splits.train.X.to_numpy().astype(np.float32),
            splits.train.y.to_numpy(),
            epochs=10,
            verbose=1,
        )

        interface = TensorFlowModel(
            model=model,
            sample_data=splits.train.X.to_numpy().astype(np.float32),
        )

        modelcard = ModelCard(
            interface=interface,
            info=self.info,
            datacard_uid=datacard.uid,
            to_onnx=True,
        )
        self.registries.model.register_card(card=modelcard)

    def test_onnx_model(self):
        """This shows how to load a modelcard and the associated model and onnx model (if converted to onnx)"""

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        modelcard: ModelCard = self.registries.model.load_card(name=self.info.name)

        # load data for testing
        datacard.load_data()

        # load onnx model
        modelcard.load_onnx_model()
        modelcard.load_model()

        splits = datacard.split_data()
        inputs = splits.train.X.to_numpy()[:1].astype(np.float32)

        print(modelcard.onnx_model.sess.run(None, {"dense_input": inputs}))

    def run_workflow(self):
        """Helper method for executing workflow"""
        self.create_datacard()
        self.create_modelcard()
        self.test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="tensorflow", repository="opsml", contact="user@email.com")
    workflow = OpsmlTensorFlowWorkflow(info=info)
    workflow.run_workflow()
