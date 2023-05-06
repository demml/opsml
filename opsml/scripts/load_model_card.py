from pathlib import Path
from typing import Optional, cast

import click

from opsml.helpers.logging import ArtifactLogger
from opsml.model.types import ModelDownloadInfo, ModelMetadata
from opsml.registry import CardRegistry, ModelCard

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
        self._base_path = base_path
        self._dir_path: Optional[Path] = None
        self.registry = registry

    @property
    def dir_path(self) -> Path:
        if self._dir_path is not None:
            return self._dir_path
        raise ValueError("No dir_path set")

    @dir_path.setter
    def dir_path(self, dir_path: Path):
        self._dir_path = dir_path

    @property
    def base_path(self) -> str:
        return self._base_path

    def _set_path(self, version: str) -> None:
        path = Path(f"{self.base_path}/onnx_model/{self.model_info.name}/v{version}/")
        path.mkdir(parents=True, exist_ok=True)
        self.dir_path = path

    def _write_api_json(self, api_def: ModelMetadata) -> None:
        save_path = self.dir_path / MODEL_FILE

        with save_path.open("w", encoding="utf-8") as file_:
            file_.write(api_def.json())
        logger.info(
            "Saved api model def to %s",
            save_path.absolute().as_posix(),
        )

    def _save_api_def(self, api_def: ModelMetadata):
        if self.model_info.name is None:
            self.model_info.name = api_def.model_name

        self._write_api_json(api_def=api_def)

    def load_and_save_model(self, version: Optional[str] = None):
        model_card = cast(
            ModelCard,
            self.registry.load_card(
                name=self.model_info.name,
                team=self.model_info.team,
                version=self.model_info.version,
                uid=self.model_info.uid,
            ),
        )

        api_def = self._get_model_api_def(model_card=model_card)

        self._save_api_def(api_def=api_def)

    def _save_onnx(self, model_definition: bytes) -> str:
        save_path = self.dir_path / "model.onnx"
        with save_path.open("wb") as file_:
            file_.write(model_definition)

        return save_path.absolute().as_posix()

    def _get_model_api_def(self, model_card: ModelCard) -> ModelMetadata:
        """Gets Onnx model api definition"""

        onnx_model = model_card.onnx_model()

        self._set_path(version=onnx_model.model_version)
        onnx_proto_path = self._save_onnx(model_definition=onnx_model.model_definition)

        if model_card.onnx_model_def is not None:
            return ModelMetadata(
                model_name=model_card.name,
                model_type=model_card.model_type,
                onnx_uri=onnx_proto_path,
                model_uri=model_card.trained_model_uri,
                onnx_version=model_card.onnx_model_def.onnx_version,
                model_version=model_card.version,
                sample_data=model_card._get_sample_data_for_api(),  # pylint: disable=protected-access
                data_schema=model_card.data_schema,
            )
        raise ValueError("No onnx definition defined")

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
