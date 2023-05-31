import pathlib
from typing import Dict, Union

import typer
from rich.console import Console
from rich.table import Table

from opsml.cli.utils import TRACKING_URI, CliApiClient, RegistryTableNames
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

app = typer.Typer()
api_client = CliApiClient()


@app.command()
def download_model(
    name: str = typer.Option(default=None, help="Name of ModelCard"),
    team: str = typer.Option(default=None, help="Team associated with ModelCard"),
    version: str = typer.Option(default=None, help="Version of ModelCard"),
    uid: str = typer.Option(default=None, help="Uid of ModelCard"),
    onnx: bool = typer.Option(default=True, help="Whether to download onnx model or original model"),
    write_dir: str = typer.Option(default="./models"),
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
        write_dir:
            Directory to write to (required)

    Example:

        ```bash
        opsml-cli download-model --name "linear-reg" --team "mlops" --write-dir ".models" --no-onnx # original model
        opsml-cli download-model --name "linear-reg" --team "mlops" --write-dir ".models" --onnx # onnx model
        opsml-cli download-model --name "linear-reg" --team "mlops" --version "1.0.0" --write-dir "./models"
        ```

    """

    path = pathlib.Path(write_dir)
    path.mkdir(parents=True, exist_ok=True)

    metadata = api_client.download_metadata(
        payload={"name": name, "version": version, "team": team, "uid": uid},
        path=path,
    )

    if onnx:
        model_path = str(metadata.get("onnx_uri"))
    else:
        model_path = str(metadata.get("model_uri"))

    api_client.download_model(
        filepath=model_path,
        write_path=path,
    )


@app.command()
def download_model_metadata(
    name: str = typer.Option(default=None),
    team: str = typer.Option(default=None),
    version: str = typer.Option(default=None),
    uid: str = typer.Option(default=None),
    write_dir: str = typer.Option(default="./model"),
):
    """
    Downloads model metadata associated with a model card

    Args:
        name:
            Card name
        team:
            Team name
        version:
            Version to search
        uid:
            Uid of Card
        write_dir:
            Director to write to

    Example:

        ```bash
        opsml-cli download-model-metadata --name "linear-reg" --team "mlops" --write-dir ".models"
        opsml-cli download-model-metadata --name "linear-reg" --team "mlops" --version "1.0.0" --write-dir ".models"
        ```

    """

    path = pathlib.Path(write_dir)
    path.mkdir(parents=True, exist_ok=True)

    api_client.download_metadata(
        payload={"name": name, "version": version, "team": team, "uid": uid},
        path=path,
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
    max_date: str = typer.Option(default=None),
    limit: int = typer.Option(default=None),
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
        max_date:
            Max date to search
        limit:
            Max number of records to return

    Example:

        ```bash
        opsml-cli list-cards --name "linear-reg" --team "mlops" --max-date "2023-05-01"
        ```

    """

    registry_name = getattr(RegistryTableNames, registry.upper())

    if registry_name is None:
        raise ValueError(
            f"No registry found. Accepted values are 'model', 'data', 'pipeline', and 'run'. Found {registry}",
            registry,
        )

    payload: Dict[str, Union[str, int]] = {
        "name": name,
        "version": version,
        "team": team,
        "uid": uid,
        "limit": limit,
        "max_date": max_date,
        "table_name": registry_name,
    }
    cards = api_client.list_cards(payload=payload)

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


@app.command()
def get_model_metrics(
    name: str = typer.Option(default=None, help="Model name"),
    team: str = typer.Option(default=None, help="Team associated with model"),
    version: str = typer.Option(default=None, help="Model Version"),
    uid: str = typer.Option(default=None, help="Model uid"),
):
    if all(bool(val) for val in [name, team, version, uid]):
        raise ValueError("A combination of name, team, version and uid must be supplied")

    payload: Dict[str, Union[str, int]] = {
        "name": name,
        "version": version,
        "team": team,
        "uid": uid,
    }

    metrics = api_client.get_metrics(payload=payload)

    table = Table(title="Model Metrics")
    table.add_column("Metric", no_wrap=True)
    table.add_column("Value")
    table.add_column("Step")
    table.add_column("Timestamp", justify="right")

    for _, metric_list in metrics.items():
        for metric in metric_list:
            table.add_row(
                str(metric.get("name")),
                str(metric.get("value")),
                str(metric.get("step", "None")),
                str(metric.get("timestamp", "None")),
            )
    console.print(table)


@app.command()
def get_data_profile(
    name: str = typer.Option(default=None, help="Model name"),
    team: str = typer.Option(default=None, help="Team associated with model"),
    version: str = typer.Option(default=None, help="Model Version"),
    uid: str = typer.Option(default=None, help="Model uid"),
    write_dir: str = typer.Option(default="./data_profile", help="Directory to write data profile to"),
):
    if all(bool(val) for val in [name, team, version, uid]):
        raise ValueError("A combination of name, team, version and uid must be supplied")

    payload: Dict[str, Union[str, int]] = {
        "name": name,
        "version": version,
        "team": team,
        "uid": uid,
    }

    path = pathlib.Path(write_dir)
    path.mkdir(parents=True, exist_ok=True)

    api_client.download_data_profile(write_path=path, payload=payload)


@app.command()
def launch_server():
    typer.launch(TRACKING_URI)


if __name__ == "__main__":
    app()
