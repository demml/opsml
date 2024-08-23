# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

import tempfile
from pathlib import Path
from typing import Any, Dict

import joblib
from fastapi import APIRouter, HTTPException, Request, status

from opsml.helpers.logging import ArtifactLogger
from opsml.storage.client import StorageClientBase
from opsml.types import RegistryTableNames, SaveName

logger = ArtifactLogger.get_logger()


router = APIRouter()


@router.get("/runs/graphs", name="graphs")
async def get_graph_plots(request: Request, repository: str, name: str, version: str) -> Dict[str, Any]:
    """Method for loading plots for a run

    Args:
        request:
            The incoming HTTP request.
        repository:
            The repository name.
        name:
            The run name.
        version:
            The run version.

    Returns:
        Dict[str, str]: A dictionary of plot names and their corresponding plots.
    """
    storage_client: StorageClientBase = request.app.state.storage_client
    storage_root = request.app.state.storage_root

    loaded_graphs: Dict[str, Any] = {}
    uri = Path(f"{storage_root}/{RegistryTableNames.RUN.value}/{repository}/{name}/v{version}")
    graph_path = uri / SaveName.GRAPHS.value

    path_exists = storage_client.exists(graph_path)

    # skip if path does not exist
    if not path_exists:
        return loaded_graphs

    paths = storage_client.ls(graph_path)

    logger.debug("Found {} graphs in {}", paths, graph_path)

    if paths:
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                for path in paths:
                    assert isinstance(path, Path)

                    rpath = graph_path / Path(path).name
                    lpath = Path(tmp_dir) / rpath.name

                    storage_client.get(rpath, lpath)
                    graph: Dict[str, Any] = joblib.load(lpath)
                    loaded_graphs[graph["name"]] = graph

            return loaded_graphs

        except Exception as error:
            logger.error(f"Failed to load graphs: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{error}") from error

    return loaded_graphs
