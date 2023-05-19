import typer
from typing import Annotated, Dict
from opsml.helpers.request_helpers import ApiRoutes, ApiClient
from opsml.registry.sql.settings import settings
from opsml.registry import CardRegistry

app = typer.Typer()


def _download_metadata(request_client: ApiClient, payload: Dict[str, str]):
    return request_client.stream_post_request(
        route=ApiRoutes.DOWNLOAD_MODEL_METADATA,
        json=payload,
    )


def _download_model(request_client: ApiClient, filepath: str):
    filepath_split = filepath.split("/")
    filename = filepath_split[-1]
    read_dir = "/".join(filepath_split[:-1])

    request_client.stream_download_file_request(
        route=ApiRoutes.DOWNLOAD_FILE,
        local_dir="models",
        filename=filename,
        read_dir=read_dir,
    )


@app.command()
def download_model(
    name: Annotated[str, typer.Option()] = None,
    team: Annotated[str, typer.Option()] = None,
    version: Annotated[str, typer.Option()] = None,
    uid: Annotated[str, typer.Option()] = None,
    onnx: Annotated[bool, typer.Option()] = True,
):
    if settings.request_client is not None:
        metadata = _download_metadata(
            request_client=settings.request_client,
            payload={"name": name, "version": version, "team": team, "uid": uid},
        )

        if onnx:
            model_path = metadata.get("onnx_uri")
        else:
            model_path = metadata.get("model_uri")

        return _download_model(
            request_client=settings.request_client,
            filepath=model_path,
        )
    else:
        raise ValueError(
            """No HTTP URI detected. Command line client is intended to work directly with HTTP""",
        )


if __name__ == "__main__":
    app()
