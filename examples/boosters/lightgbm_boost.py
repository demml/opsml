from typing import Any, Dict

import lightgbm as lgb
from sklearn.preprocessing import StandardScaler

from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    LightGBMModel,
    ModelCard,
    PandasData,
)
from opsml.helpers.data import create_fake_data


class OpsmlLightGBMBoosterWorkflow:
    def __init__(self, info: CardInfo, params: Dict[str, Any]):
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
        self.params = params

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

        # Create datacard
        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the LightGBMModel.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)

        # load data from server
        datacard.load_data()

        # split data
        data = datacard.split_data()

        # create standard scaler
        scaler = StandardScaler()
        scaler.fit(data.train.X)

        X_train = scaler.transform(data.train.X)
        X_test = scaler.transform(data.test.X)

        lgb_train = lgb.Dataset(X_train, data.train.y)
        lgb_eval = lgb.Dataset(X_test, data.test.y, reference=lgb_train)

        # fit model
        gbm = lgb.train(
            params,
            lgb_train,
            num_boost_round=20,
            valid_sets=lgb_eval,
            callbacks=[lgb.early_stopping(stopping_rounds=5)],
        )

        # fit model
        interface = LightGBMModel(
            model=gbm,
            sample_data=X_train[:100],
            preprocessor=scaler,
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

        # split data
        data = datacard.split_data()

        # load model
        modelcard.load_model()

        # load onnx model
        modelcard.load_onnx_model()

        prediction = modelcard.onnx_model.sess.run(None, {"predict": data.test.X.to_numpy()[:5]})
        print(prediction)

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="lightgbm", repository="opsml", contact="user@email.com")
    params = {
        "boosting_type": "gbdt",
        "objective": "regression",
        "metric": {"l2", "l1"},
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": 0,
    }
    workflow = OpsmlLightGBMBoosterWorkflow(info=info, params=params)
    workflow.run_workflow()
