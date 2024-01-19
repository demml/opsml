import lightning as L
import numpy as np
import torch

from examples.torch.lightning_module import RegressionModel, SimpleDataset
from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    LightningModel,
    ModelCard,
    TorchData,
    TorchOnnxArgs,
)


class OpsmlLightningWorkflow:
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

        This example highlights the uses of the TorchData interface
        """

        # create fake data
        x = torch.Tensor(np.arange(10000)).reshape(-1, 1)
        y = x * 2

        # Create data interface
        data_interface = TorchData(data=torch.concatenate((x, y), dim=1))

        # Create datacard
        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the LightningModel.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

        # load data from server
        datacard.load_data()

        X = datacard.data[:, 0].reshape(-1, 1)
        y = datacard.data[:, 1].reshape(-1, 1)

        dataset = SimpleDataset(X, y)
        model = RegressionModel()
        model.dataset = dataset

        trainer = L.Trainer(max_epochs=10)
        trainer.fit(model)

        # lightning interface
        interface = LightningModel(
            model=trainer,
            sample_data=X,
            onnx_args=TorchOnnxArgs(
                input_names=["predict"],
                output_names=["output"],
                dynamic_axes={"predict": {0: "batch_size"}},  # allow for >=1 batch size
            ),
        )

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

        # load onnx model
        modelcard.load_onnx_model()
        modelcard.load_model(model_arch=RegressionModel)

        inputs = datacard.data.numpy()[:2, 0].reshape(-1, 1)
        print(modelcard.onnx_model.sess.run(None, {"predict": inputs}))

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="torch", repository="opsml", contact="user@email.com")
    workflow = OpsmlLightningWorkflow(info=info)
    workflow.run_workflow()
