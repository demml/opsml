import lightgbm as lgb
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    LightGBMModel,
    ModelCard,
    PandasData,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data


class OpsmlLightGBMSklearnWorkflow:
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
        self.cat_cols = ["cat_col_0", "cat_col_1"]

    def _create_datacard(self):
        """Shows how to create a data interface and datacard

        You can think of cards as outputs to each step in your workflow.
        In your data getting step, you will get your data, create a data interface,
        and then create/register a datacard, which will be stored in the registry.

        This example highlights the uses of the PandasData interface
        """

        # create fake data
        X, y = create_fake_data(n_samples=1000, n_categorical_features=2, task_type="regression")
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

    def _create_pipeline_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the LightGBMModel.
        """

        categorical_transformer = Pipeline([("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))])
        preprocessor = ColumnTransformer(
            transformers=[("cat", categorical_transformer, self.cat_cols)],
            remainder="passthrough",
        )

        # setup lgb regressor
        pipe = Pipeline([("preprocess", preprocessor), ("rf", lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5))])

        # split data
        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        data = datacard.split_data()

        # fit
        pipe.fit(data.train.X, data.train.y)

        # create model interface
        interface = SklearnModel(
            model=pipe,
            sample_data=data.train.X,
            task_type="regression",  # optional
        )

        # create modelcard
        modelcard = ModelCard(interface=interface, info=info, datacard_uid=datacard.uid, to_onnx=True)
        self.registries.model.register_card(card=modelcard)

    def _create_lightgbm_modelcard(self):
        """This is an arbitrary example of how to create a modelcard for a lightgbm model only
        Notice we use the LightGBMModel interface
        """

        # split data
        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        data = datacard.split_data()

        reg = lgb.LGBMRegressor(n_estimators=3, max_depth=3, num_leaves=5)

        # fit
        # Only using the first 5 numerical features for convenience
        reg.fit(data.train.X.to_numpy()[:, 0:5], data.train.y.to_numpy())

        # create model interface
        interface = LightGBMModel(model=reg, sample_data=data.train.X.to_numpy()[:, 0:5])

        # create modelcard
        # Here we are registering the pipeline which contains an sklearn model
        modelcard = ModelCard(
            name="lgb-reg",
            repository="opsml",
            contact="user@email.com",
            interface=interface,
            datacard_uid=datacard.uid,
            to_onnx=True,
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

        inputs = {}
        for c in data.test.X.columns:
            values = data.test.X[c][:1].values
            if c in self.cat_cols:
                values = values.astype(str).reshape(-1, 1)
            else:
                values = values.astype(np.float32).reshape(-1, 1)
            inputs[c] = values

        print(modelcard.onnx_model.sess.run(None, inputs))

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_pipeline_modelcard()
        self._create_lightgbm_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # set info (easier than specifying in each card)
    info = CardInfo(name="lightgbm", repository="opsml", contact="user@email.com")
    workflow = OpsmlLightGBMSklearnWorkflow(info=info)
    workflow.run_workflow()
