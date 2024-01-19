import uuid
from pathlib import Path
from typing import Tuple, cast

from numpy.typing import NDArray
from sklearn import tree

from opsml.cards import ModelCard
from opsml.model import SklearnModel
from opsml.storage import client
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName


def test_model_interface(
    regression_data: Tuple[NDArray, NDArray],
    api_storage_client: client.StorageClientBase,
):
    class SubclassModel(SklearnModel):
        @property
        def model_class(self) -> str:
            return "SubclassModel"

        @staticmethod
        def name() -> str:
            return SubclassModel.__name__

    X, y = regression_data
    reg = tree.DecisionTreeRegressor(max_depth=5).fit(X, y)
    model = SubclassModel(model=reg, sample_data=X)

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
        datacard_uid=uuid.uuid4().hex,
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(modelcard)

    # check paths exist on server
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "repository": modelcard.repository,
            "version": modelcard.version,
        },
        registry_type=RegistryType.MODEL,
    )

    loaded_card = cast(ModelCard, loader.load_card(interface=SubclassModel))
    assert isinstance(loaded_card, ModelCard)

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    assert loaded_card.interface.model_class == modelcard.interface.model_class
