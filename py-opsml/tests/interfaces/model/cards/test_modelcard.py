from opsml.model import SklearnModel
from opsml.core import Tags
from opsml.card import ModelCard
from pathlib import Path
from opsml.core import OpsmlStorageSettings
import shutil


def test_save_model_interface(tmp_path: Path, random_forest_classifier: SklearnModel):
    interface: SklearnModel = random_forest_classifier

    save_path = tmp_path / "test"
    save_path.mkdir()

    tags = Tags()

    tags.add_tag("foo", "bar")
    tags.add_tag("baz", "qux")

    card = ModelCard(
        interface=interface,
        repository="test",
        name="test",
        contact="test",
        to_onnx=True,
        tags=tags,
    )

    # save all assets to path (including card)
    # card.save(save_path)


#
# settings = OpsmlStorageSettings()
# fs = FileSystemStorage(settings)
#
# files = fs.find(save_path)
# assert len(files) == 5
#
## put all assets to path (including card)
# fs.put(save_path, card.uri, recursive=True)
#
## use storage client to upload assets to cloud storage
# files = fs.find(card.uri)
# assert len(files) == 5
#
## get all assets from path (including card)
# download_path = tmp_path / "download"
# fs.get(download_path, card.uri, recursive=True)
#
## assert all assets are downloaded
# files = fs.find(download_path)
# assert len(files) == 5
#
## load card from path
# loaded_card = ModelCard.model_validate_json(card.model_dump_json())
#
# assert loaded_card.interface.model is None
# assert loaded_card.interface.sample_data is None
#
# loaded_card.load(
#    path=download_path,
#    model=True,
#    sample_data=True,
# )
#
# assert loaded_card.interface.model is not None
# assert loaded_card.interface.sample_data is not None
#
## delete ./opsml_repo
# shutil.rmtree(settings.storage_uri)
#
