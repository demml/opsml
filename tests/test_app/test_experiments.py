from opsml_artifacts import DataCard, ModelCard
from unittest.mock import patch
from pathlib import Path


def test_mlflow(mlflow_experiment, sklearn_pipeline, mock_pathlib):

    with mlflow_experiment as exp:

        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        exp.register_card(card=data_card)

        print(data_card.data_uri)
        a

        model_card1 = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid=data_card.uid,
        )

        exp.register_card(card=model_card1)
        loaded_card = exp.load_card(card_type="model", uid=model_card1.uid)
