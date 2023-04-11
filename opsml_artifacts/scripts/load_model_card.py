from pathlib import Path
from typing import Optional, cast

import click

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry import CardRegistry, ModelCard
from opsml_artifacts.registry.model.types import ModelApiDef, ModelDownloadInfo

logger = ArtifactLogger.get_logger(__name__)

BASE_SAVE_PATH = "app"
MODEL_FILE = "model_def.json"


class ModelLoader:
    """Class for loading ModelCard Onnx definition"""

    def __init__(
        self,
        model_info: ModelDownloadInfo,
        registry: CardRegistry,
        base_path: str = BASE_SAVE_PATH,
    ):

        self.model_info = model_info
        self.base_path = base_path
        self._file_path: Optional[str] = None
        self.registry = registry

    @property
    def file_path(self) -> str:
        return str(self._file_path)

    @file_path.setter
    def file_path(self, file_path: str):
        self._file_path = file_path

    def _set_path(self, api_def: ModelApiDef) -> Path:
        path = Path(f"{self.base_path}/onnx_model/{self.model_info.name}/v{api_def.model_version}/")
        path.mkdir(parents=True, exist_ok=True)
        return path / MODEL_FILE

    def _write_api_json(self, api_def: ModelApiDef, filepath: Path) -> None:

        with filepath.open("w", encoding="utf-8") as file_:
            file_.write(api_def.json())
        logger.info("Saved api model def to %s", filepath)

    def _save_api_def(self, api_def: ModelApiDef):
        if self.model_info.name is None:
            self.model_info.name = api_def.model_name

        filepath = self._set_path(api_def=api_def)
        self._write_api_json(api_def=api_def, filepath=filepath)
        path = filepath.absolute().as_posix()
        self.file_path = path

    def load_and_save_model(self, version: Optional[str] = None):
        model_card = self.registry.load_card(
            name=self.model_info.name,
            team=self.model_info.team,
            version=self.model_info.version,
            uid=self.model_info.uid,
        )

        api_def = self._get_model_api_def(model_card=cast(ModelCard, model_card))
        self._save_api_def(api_def=api_def)

    def _get_model_api_def(self, model_card: ModelCard) -> ModelApiDef:
        onnx_model = model_card.onnx_model()
        api_model = onnx_model.get_api_model()

        return api_model

    def save_to_local_file(self) -> None:
        self.load_and_save_model()


@click.command()
@click.option("--name", help="Name of the model", default=None, required=False, type=str)
@click.option("--team", help="Name of team that model belongs to", default=None, required=False, type=str)
@click.option("--version", help="Version of model to load", default=None, required=False, type=str)
@click.option("--uid", help="Unique id of modelcard", default=None, required=False, type=str)
def load_model_card_to_file(name: str, team: str, version: str, uid: str):
    if uid is None:
        if not all(bool(arg) for arg in [name, team]):
            raise ValueError(
                """A uid is required if name and team are not specified
           """
            )
    model_info = ModelDownloadInfo(
        name=name,
        team=team,
        version=version,
        uid=uid,
    )
    model_registry = CardRegistry(registry_name="model")
    loader = ModelLoader(
        model_info=model_info,
        registry=model_registry,
    )
    loader.save_to_local_file()


if __name__ == "__main__":
    load_model_card_to_file()  # pylint: disable=no-value-for-parameter
