from opsml_artifacts import DataCard, ModelCard
from unittest.mock import patch
from pathlib import Path


def test_mlflow(mlflow_experiment, sklearn_pipeline):

    with mlflow_experiment as exp:

        model, data = sklearn_pipeline
        data_card = DataCard(
            data=data,
            name="pipeline_data",
            team="mlops",
            user_email="mlops.com",
        )
        exp.register_card(card=data_card)

        model_card = ModelCard(
            trained_model=model,
            sample_input_data=data[0:1],
            name="pipeline_model",
            team="mlops",
            user_email="mlops.com",
            data_card_uid=data_card.uid,
        )

        #
        exp.register_card(card=model_card)
        loaded_card = exp.load_card(card_type="model", uid=model_card.uid)
        loaded_card.load_trained_model()

        assert loaded_card.data_card_uid == model_card.data_card_uid
        load_data = loaded_card = exp.load_card(card_type="data", uid=data_card.uid)
