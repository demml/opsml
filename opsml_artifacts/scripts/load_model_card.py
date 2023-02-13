from typing import Optional

import click
import joblib

from opsml_artifacts import CardRegistry
from opsml_artifacts.registry.cards.artifact_storage import (
    save_record_artifact_to_storage,
)
from opsml_artifacts.registry.cards.storage_system import LocalStorageClient
from opsml_artifacts.registry.cards.types import SaveInfo
from opsml_artifacts.registry.sql.registry import SQLRegistry

from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate


class ModelLoader:
    def __init__(
        self,
        storage_type: str,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ):

        self.registry = self._set_registry(storage_type=storage_type)
        self.model_card = self.registry.load_card(name=name, team=team, version=version, uid=uid)
        self.storage_client = LocalStorageClient(connection_args={}, base_path_prefix=f"app")

    def _set_registry(self, storage_type: str) -> SQLRegistry:
        return CardRegistry(registry_name="model", connection_type=storage_type)

    def save_to_local_file(self) -> str:
        onnx_model = self.model_card.onnx_model()

        output = Path("onnx_model/")
        output.mkdir(parents=True, exist_ok=True)
        output = output.parent.joinpath("input_model.py")
        print(output)
        # generate(
        #    onnx_model.input_sig.schema_json(),
        #    input_file_type=InputFileType.JsonSchema,
        #    output=output,
        # )


#
# model: str = output.read_text()
# print(model)
# save_info = SaveInfo(
#    blob_path="onnx_model",
#    name=self.model_card.name,
#    team=self.model_card.team,
#    version=self.model_card.version,
# )
# storage_path = save_record_artifact_to_storage(
#    artifact=onnx_model,
#    save_info=save_info,
#    storage_client=self.storage_client,
#    artifact_type="joblib",
# )
# return storage_path.uri


@click.command()
@click.option("--name", help="Name of the model", required=False, type=str)
@click.option("--team", help="Name of team that model belongs to", required=False, type=str)
@click.option("--version", help="Version of model to load", required=False, type=int)
@click.option("--uid", help="Unique id of modelcard", required=False, type=str)
@click.option(
    "--storage_type", help="Storage client to use when loading model", default="local", required=False, type=str
)
def load_model_card_to_file(name: str, team: str, version: int, uid: str, storage_type: str):
    click.echo(f"{name}, {team}, {version}")
    if uid is None:
        if not all([bool(arg) for arg in [name, team, version]]):
            raise ValueError(
                """A uid is required if any of name, team and version are missing
            """
            )

        loader = ModelLoader(storage_type="local", name=name, team=team, version=version, uid=uid)
        storage_uri = loader.save_to_local_file()

        click.echo(f"Saved onnx predictor to {storage_uri}")


if __name__ == "__main__":
    load_model_card_to_file()
