# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import pathlib
from typing import Any, Dict, List, Union

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from opsml.cli.utils import TRACKING_URI, ApiRoutes, CliApiClient, RegistryTableNames
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

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
    tag_key: str = typer.Option(default=None),
    tag_value: str = typer.Option(default=None),
    max_date: str = typer.Option(default=None),
    limit: int = typer.Option(default=None),
    ignore_release_candidates: bool = typer.Option(default=False),
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
        tag_key:
            Tag key
        tag_value:
            Tag value
        max_date:
            Max date to search
        limit:
            Max number of records to return
        ignore_release_candidates:
            Whether to ignore release candidates

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

    if tag_key is not None:
        tags = {tag_key: tag_value}
    else:
        tags = None

    payload: Dict[str, Union[str, int, Dict[str, str]]] = {
        "name": name,
        "version": version,
        "team": team,
        "uid": uid,
        "limit": limit,
        "max_date": max_date,
        "tags": tags,
        "table_name": registry_name,
    }
    print(payload)
    cards = api_client.list_cards(payload=payload)

    table = Table(title=f"{registry_name} cards")
    table.add_column("Name", no_wrap=True)
    table.add_column("Team")
    table.add_column("Date")
    table.add_column("User Email")
    table.add_column("Version")
    table.add_column("Tags")
    table.add_column("Uid", justify="right")

    for card in cards:
        table.add_row(
            card.get("name"),
            card.get("team"),
            card.get("date"),
            card.get("user_email"),
            card.get("version"),
            str(card.get("tags")),
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
    """
    Prints metrics associated with a ModelCard

    Args:
        name:
            Card name
        team:
            Team name
        version:
            Version to search
        uid:
            Uid of Card

    Example:

        ```bash
        opsml-cli get-model-metrics --name "linear-reg" --team "mlops" --version "1.0.0"
        ```

    """
    if uid is None and not all(bool(val) for val in [name, team, version]):
        raise ValueError("A combination of (name, team, version) and uid must be supplied")

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
def download_data_profile(
    name: str = typer.Option(default=None, help="Data name"),
    team: str = typer.Option(default=None, help="Team associated with data"),
    version: str = typer.Option(default=None, help="Data Version"),
    uid: str = typer.Option(default=None, help="Data uid"),
    write_dir: str = typer.Option(default="./data_profile", help="Directory to write data profile to"),
):
    """
    Downloads a data profile from a DataCard

    Args:
        name:
            Card name
        team:
            Team name
        version:
            Card version
        uid:
            Card uid
        write_dir:
            Directory to write data profile to

    Returns
        HTML file

    Example:

        ```bash
        opsml-cli download-data-profile --name "linear-reg" --team "mlops" --version "1.0.0"
        ```
    """

    if uid is None and not all(bool(val) for val in [name, team, version]):
        raise ValueError("A combination of name, team, version and uid must be supplied")

    payload: Dict[str, Union[str, int, List[str]]] = {
        "name": name,
        "version": version,
        "team": team,
        "uid": uid,
    }

    path = pathlib.Path(write_dir)
    path.mkdir(parents=True, exist_ok=True)

    api_client.stream_data_file(
        path=ApiRoutes.DATA_PROFILE,
        write_path=path,
        payload=payload,
    )


@app.command()
def compare_data_profiles(
    name: str = typer.Option(default=None, help="Data name"),
    team: str = typer.Option(default=None, help="Team associated with data"),
    version: List[str] = typer.Option(default=None, help="List of data versions"),
    uid: List[str] = typer.Option(default=None, help="Data uid"),
    write_dir: str = typer.Option(default="./data_profile", help="Directory to write data profile to"),
):
    """
    Takes a list of version or uids and runs data profile comparisons

    Args:
        name:
            Card name
        team:
            Team name
        version:
            List of versions to compare
        uid:
            List of Uids to compare
        write_dir:
            Directory to write data profile to

    Returns
        HTML file

    Example:

        ```bash
        opsml-cli compare-data-profiles --name "linear-reg" --team "mlops" --version "1.0.0" --version "1.1.0"
        ```

    """
    if uid is None and not all(bool(val) for val in [name, team, version]):
        raise ValueError("A list of versions (with name and team) or uids is required")

    payload: Dict[str, Union[str, int, List[str]]] = {
        "name": name,
        "versions": version,
        "team": team,
        "uids": uid,
    }

    path = pathlib.Path(write_dir)
    path.mkdir(parents=True, exist_ok=True)

    api_client.stream_data_file(
        path=ApiRoutes.COMPARE_DATA,
        write_path=path,
        payload=payload,
    )


@app.command()
def compare_model_metrics(
    challenger_uid: str = typer.Option(default=None, help="Challenger uid"),
    champion_uid: List[str] = typer.Option(default=None, help="List of champion one or more model uids"),
    metric_name: List[str] = typer.Option(
        default=None,
        help="Name of metric to compare. This metric must already exist for a challenger and champion models",
    ),
    lower_is_better: List[str] = typer.Option(default=["True"], help="Whether a lower metric is better"),
):
    """
    Compare model metrics via `ModelChallenger`

    Args:
        challenger_uid:
            Challenger uid
        champion_uid:
            List of champion model uids
        metric_name:
            Name of metric to compare. This metric must already exist for a challenger and champion models
        lower_is_better:
            Whether a lower metric is better
    Example:

        ```bash
        opsml-cli compare-model-metrics \
            --challenger-uid "challenger-uid" \
            --champion-uid "1st-champion-uid" \
            --champion-uid "2nd-champion-uid" \
            --metric-name "mae"
        ```

    """
    lower_is_better_bool = [threshold.lower() == "true" for threshold in lower_is_better]

    payload: Dict[str, Union[str, Any]] = {
        "metric_name": metric_name,
        "lower_is_better": lower_is_better_bool,
        "challenger_uid": challenger_uid,
        "champion_uid": champion_uid,
    }

    challenger_name, challenger_version, battle_reports = api_client.compare_metrics(payload=payload)

    table = Table(title=f"Model Challenger Results for {challenger_name} v{challenger_version}")
    table.add_column("Champion \nName", justify="center")
    table.add_column("Champion \nVersion", justify="center")
    table.add_column("Metric", justify="center")
    table.add_column("Champion \nValue", justify="center")
    table.add_column("Challenger \nValue", justify="center")
    table.add_column("Challenger \nWin", justify="center")

    # print(Text(report.get("challenger_win", "None")))
    for _, reports in battle_reports.items():
        for report in reports:
            champion_metric = report.get("champion_metric")
            challenger_metric = report.get("challenger_metric")
            challenger_win = report.get("challenger_win", "None")

            if challenger_win:
                challenger_win = Text(str(challenger_win), style="green")
            else:
                challenger_win = Text(str(challenger_win), style="red")

            table.add_row(
                str(report.get("champion_name", "None")),
                str(report.get("champion_version", "None")),
                str(champion_metric.get("name", "None")),
                str(champion_metric.get("value", "None")),
                str(challenger_metric.get("value", "None")),
                challenger_win,
            )
        table.add_section()

    console.print(table)


@app.command()
def open_server():
    """Opens OPSML_TRACKING_URI"""
    typer.launch(TRACKING_URI)


@app.command()
def launch_uvicorn_app(
    run_mlflow: bool = typer.Option(default=True, help="Whether to start opsml with mlflow"),
    login: bool = typer.Option(default=False, help="Whether to use login credentials"),
    port: int = typer.Option(default=8888, help="Default port to use with the opsml server"),
):
    """
    Launches a Uvicorn Opsml server

    Args:
        run_mlflow:
            Whether to launch with mlflow
        login:
            Whether to use login credentials
        port:
            Default port to use with the opsml server
    """

    from opsml.app.main import OpsmlApp  # pylint: disable=import-outside-toplevel

    model_api = OpsmlApp(run_mlflow=run_mlflow, port=port, login=login)
    model_api.build_app()
    model_api.run()


if __name__ == "__main__":
    app()
