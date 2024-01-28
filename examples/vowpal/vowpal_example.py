import pandas as pd
import vowpalwabbit

from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    ModelCard,
    PandasData,
    VowpalWabbitModel,
)

# This example is taken from the vowpal wabbit documentation
# https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html


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

        data = [
            {
                "action": 1,
                "cost": 2,
                "probability": 0.4,
                "feature1": "a",
                "feature2": "c",
                "feature3": "",
                "split": "train",
            },
            {
                "action": 3,
                "cost": 0,
                "probability": 0.2,
                "feature1": "b",
                "feature2": "d",
                "feature3": "",
                "split": "train",
            },
            {
                "action": 4,
                "cost": 1,
                "probability": 0.5,
                "feature1": "a",
                "feature2": "b",
                "feature3": "",
                "split": "train",
            },
            {
                "action": 2,
                "cost": 1,
                "probability": 0.3,
                "feature1": "a",
                "feature2": "b",
                "feature3": "c",
                "split": "train",
            },
            {
                "action": 3,
                "cost": 1,
                "probability": 0.7,
                "feature1": "a",
                "feature2": "d",
                "feature3": "",
                "split": "train",
            },
            {
                "action": None,
                "cost": None,
                "probability": None,
                "feature1": "b",
                "feature2": "c",
                "feature3": "",
                "split": "test",
            },
            {
                "action": None,
                "cost": None,
                "probability": None,
                "feature1": "a",
                "feature2": "",
                "feature3": "b",
                "split": "test",
            },
            {
                "action": None,
                "cost": None,
                "probability": None,
                "feature1": "b",
                "feature2": "b",
                "feature3": "",
                "split": "test",
            },
            {
                "action": None,
                "cost": None,
                "probability": None,
                "feature1": "a",
                "feature2": "",
                "feature3": "b",
                "split": "test",
            },
        ]

        df = pd.DataFrame(data)

        # Add index to data frame
        df["index"] = range(1, len(df) + 1)
        df = df.set_index("index")

        # Create data interface
        data_interface = PandasData(
            data=df,
            data_splits=[
                DataSplit(label="train", column_name="split", column_value="train"),
                DataSplit(label="test", column_name="split", column_value="test"),
            ],
        )

        # Create datacard
        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the VowpalWabbitModel interface and how you can load
        and split data from a datacard.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

        # load data from server
        datacard.load_data()

        # split data
        data = datacard.split_data()
        train_df = data["train"].X
        test_df = data["test"].X

        vw = vowpalwabbit.Workspace("--cb 4 --quiet")
        for i in train_df.index:
            action = train_df.loc[i, "action"]
            cost = train_df.loc[i, "cost"]
            probability = train_df.loc[i, "probability"]
            feature1 = train_df.loc[i, "feature1"]
            feature2 = train_df.loc[i, "feature2"]
            feature3 = train_df.loc[i, "feature3"]

            # Construct the example in the required vw format.
            learn_example = (
                str(action)
                + ":"
                + str(cost)
                + ":"
                + str(probability)
                + " | "
                + str(feature1)
                + " "
                + str(feature2)
                + " "
                + str(feature3)
            )

            # Here we do the actual learning.
            vw.learn(learn_example)

        for j in test_df.index:
            feature1 = test_df.loc[j, "feature1"]
            feature2 = test_df.loc[j, "feature2"]
            feature3 = test_df.loc[j, "feature3"]

            test_example = "| " + str(feature1) + " " + str(feature2) + " " + str(feature3)

            choice = vw.predict(test_example)
            print(j, choice)

        vw.finish()

        # create model interface
        interface = VowpalWabbitModel(model=vw, sample_data=test_example)

        # create modelcard
        modelcard = ModelCard(interface=interface, info=self.info, datacard_uid=datacard.uid)
        self.registries.model.register_card(card=modelcard)

    def _test_model(self):
        """This shows how to load a modelcard and the associated model"""

        modelcard: ModelCard = self.registries.model.load_card(name=self.info.name)

        # load onnx model
        # supply CLI arguments
        # Opsml will automatically inject model filename into vw.Workspace
        modelcard.load_model(arguments="--cb 4 --quiet")
        print(modelcard.model.predict(modelcard.sample_data))

    def _continue_training(self):
        """This shows how to load the modelcard and continue training the model"""

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        modelcard: ModelCard = self.registries.model.load_card(name=self.info.name)
        modelcard.load_model(arguments="--cb 4 --quiet")

        vw = modelcard.model

        # load data from server
        datacard.load_data()

        # split data
        data = datacard.split_data()

        # learn over train data again (as an example)
        train_df = data["test"].X
        for i in train_df.index:
            action = train_df.loc[i, "action"]
            cost = train_df.loc[i, "cost"]
            probability = train_df.loc[i, "probability"]
            feature1 = train_df.loc[i, "feature1"]
            feature2 = train_df.loc[i, "feature2"]
            feature3 = train_df.loc[i, "feature3"]

            # Construct the example in the required vw format.
            learn_example = (
                str(action)
                + ":"
                + str(cost)
                + ":"
                + str(probability)
                + " | "
                + str(feature1)
                + " "
                + str(feature2)
                + " "
                + str(feature3)
            )

            # Here we do the actual learning.
            vw.learn(learn_example)
        vw.finish()

        self.registries.model.update_card(card=modelcard)

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_model()
        self._continue_training()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="vowpal-cb", repository="opsml", contact="user@email.com")

    workflow = OpsmlWorkflow(info=info)
    workflow.run_workflow()
