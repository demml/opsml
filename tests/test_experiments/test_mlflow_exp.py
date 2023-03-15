from opsml_artifacts import CardRegistry, DataCard, ModelCard
import time
from mlflow.tracking import MlflowClient


def test_mlflow_exp(mlflow_experiment, sklearn_pipeline, mock_pyarrow_parquet_write):

    with mlflow_experiment as exp:

        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        exp.register_card(card=data_card)

        model_card1 = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid=data_card.uid,
        )

        exp.register_card(card=model_card1)
        time.sleep(30)
