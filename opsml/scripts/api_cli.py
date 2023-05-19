from typing import Dict

import typer
from rich.console import Console
from rich.table import Table

from opsml.helpers.request_helpers import ApiClient, ApiRoutes
from opsml.registry.sql.settings import settings
from opsml.registry.sql.sql_schema import RegistryTableNames

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


def _list_cards(request_client: ApiClient, payload: Dict[str, str]):
    response = request_client.post_request(
        route=ApiRoutes.LIST_CARDS,
        json=payload,
    )

    return response.get("cards")


@app.command()
def download_model(
    name: str = typer.Option(default=None),
    team: str = typer.Option(default=None),
    version: str = typer.Option(default=None),
    uid: str = typer.Option(default=None),
    onnx: str = typer.Option(default=None),
):
    """
    Downloads a model (onnx or original model) associated with a model card

    Args:
        name:
            Card name
        team:
            Team name
        version:
            Version to search
        uid:
            Uid of Card
        onnx:
            Whether to return onnx model or original model (no-onnx)

    Example:
        opsml-api download-model --name "linear-reg" --team "mlops" --no-onnx # original model
        opsml-api download-model --name "linear-reg" --team "mlops" --onnx # onnx model

    """

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
    raise ValueError(
        """No HTTP URI detected. Command line client is intended to work directly with HTTP""",
    )


console = Console()


@app.command()
def list_cards(
    registry: str = typer.Option(
        ..., help="Registry to search. Accepted values are 'model', 'data', 'pipeline', and 'run'"
    ),
    name: str = typer.Option(default=None),
    team: str = typer.Option(default=None),
    version: str = typer.Option(default=None),
    uid: str = typer.Option(default=None),
):
    """
    Lists cards from a specific registry in table format

    Args:
        registry:
            Name of Card registry to search. Accepted values are 'model', 'data', 'pipeline', and 'run'
        name:
            Card name
        team:
            Team name
        version:
            Version to search
        uid:
            Uid of Card

    Example:
        opsml-api list-card --name "linear-reg" --team "mlops"

    """
    registry_name = getattr(RegistryTableNames, registry.upper())

    if registry_name is None:
        raise ValueError(
            f"No registry found. Accepted values are 'model', 'data', 'pipeline', and 'run'. Found {registry}",
            registry,
        )
    if settings.request_client is not None:
        cards = _list_cards(
            request_client=settings.request_client,
            payload={
                "name": name,
                "version": version,
                "team": team,
                "uid": uid,
                "table_name": registry_name,
            },
        )

        table = Table(title=f"{registry_name} cards")
        table.add_column("Name", no_wrap=True)
        table.add_column("Team")
        table.add_column("Date")
        table.add_column("User Email")
        table.add_column("Version")
        table.add_column("Uid", justify="right")

        for card in cards:
            table.add_row(
                card.get("name"),
                card.get("team"),
                card.get("date"),
                card.get("user_email"),
                card.get("version"),
                card.get("uid"),
            )
        console.print(table)

    else:
        raise ValueError(
            """No HTTP URI detected. Command line client is intended to work directly with HTTP""",
        )


if __name__ == "__main__":
    app()
