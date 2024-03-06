# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import joblib
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from opsml.app.routes.pydantic_models import AuditReport
from opsml.app.routes.utils import (
    get_names_repositories_versions,
    list_repository_name_info,
)
from opsml.cards.audit import AuditCard, AuditSections
from opsml.cards.base import ArtifactCard
from opsml.cards.data import DataCard
from opsml.cards.model import ModelCard
from opsml.cards.run import RunCard
from opsml.data.interfaces import DataInterface
from opsml.helpers.logging import ArtifactLogger
from opsml.model import ModelInterface
from opsml.registry import CardRegistry
from opsml.storage import client
from opsml.types import ModelMetadata, SaveName, Suffix

logger = ArtifactLogger.get_logger()

# Constants
TEMPLATE_PATH = Path(__file__).parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATE_PATH)


class RouteHelper:
    def _check_version(
        self,
        registry: CardRegistry,
        name: str,
        versions: List[Dict[str, Any]],
        version: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[ArtifactCard, str]:
        """Load card from version

        Args:
            registry:
                The card registry.
            name:
                The card name.
            versions:
                The list of card versions.
            version:
                The card version.

        Returns:
            `ArtifactCard` and `str`
        """
        if version is None:
            selected_card = registry.load_card(uid=versions[0]["uid"], **kwargs)
            version = selected_card.version

            return selected_card, str(version)

        return registry.load_card(name=name, version=version), version


class AuditRouteHelper(RouteHelper):
    """Route helper for AuditCard pages"""

    def get_homepage(self, request: Request) -> _TemplateResponse:
        """Returns default audit page when all parameters are None

        Args:
            request:
                The incoming HTTP request.

        Returns:
            `templates.TemplateResponse`

        """
        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "repositories": request.app.state.registries.model._registry.unique_repositories,
                "models": None,
                "selected_repository": None,
                "selected_model": None,
                "version": None,
                "audit_report": None,
            },
        )

    def get_repository_page(self, request: Request, repository: str) -> _TemplateResponse:
        """Returns audit page for a specific repository

        Args:
            request:
                The incoming HTTP request.
            repository:
                The repository name.
        """
        repositories = request.app.state.registries.model._registry.unique_repositories
        model_names = request.app.state.registries.model._registry.get_unique_card_names(repository=repository)
        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "repositories": repositories,
                "selected_repository": repository,
                "models": model_names,
                "versions": None,
                "selected_model": None,
                "version": None,
                "audit_report": None,
            },
        )

    def get_versions_page(self, request: Request, name: str, repository: str) -> _TemplateResponse:
        """Returns the audit page for a model name, repository, and versions

        Args:
            request:
                The incoming HTTP request.
            name:
                The model name.
            repository:
                The repository name.
        """
        model_names, repositories, versions = get_names_repositories_versions(
            registry=request.app.state.registries.model,
            name=name,
            repository=repository,
        )

        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "repositories": repositories,
                "selected_repository": repository,
                "models": model_names,
                "selected_model": name,
                "versions": versions,
                "version": None,
                "audit_report": None,
            },
        )

    def _get_audit_report(
        self,
        audit_registry: CardRegistry,
        uid: Optional[str] = None,
    ) -> AuditReport:
        """Retrieves audit report. If uid is None, returns empty audit report.

        Args:
            audit_registry:
                Audit registry.
            uid:
                Audit uid.

        Returns:
            `AuditReport`
        """

        if uid is None:
            return AuditReport(
                name=None,
                repository=None,
                contact=None,
                version=None,
                uid=None,
                status=False,
                audit=AuditSections().model_dump(),  # type: ignore
                timestamp=None,
                comments=[],
            )

        audit_card: AuditCard = audit_registry.load_card(uid=uid)  # type: ignore
        return AuditReport(
            name=audit_card.name,
            repository=audit_card.repository,
            contact=audit_card.contact,
            version=audit_card.version,
            uid=audit_card.uid,
            status=audit_card.approved,
            audit=audit_card.audit.model_dump(),
            timestamp=None,
            comments=audit_card.comments,
        )

    def get_name_version_page(
        self,
        request: Request,
        repository: str,
        name: str,
        version: Optional[str] = None,
        contact: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> _TemplateResponse:
        """Get audit information for model version

        Args:
            request:
                The incoming HTTP request.
            repository:
                The repository name.
            name:
                The model name.
            version:
                The model version.
            uid:
                The model uid.
            contact:
                The user contact.
        """

        model_names, repositories, versions = get_names_repositories_versions(
            registry=request.app.state.registries.model,
            name=name,
            repository=repository,
        )

        model_record = request.app.state.registries.model.list_cards(
            name=name,
            version=version,
            uid=uid,
        )[0]

        contact = model_record.get("contact") if contact is None else contact

        audit_report = self._get_audit_report(
            audit_registry=request.app.state.registries.audit,
            uid=model_record.get("auditcard_uid"),
        )

        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "repositories": repositories,
                "selected_repository": repository,
                "models": model_names,
                "selected_model": name,
                "selected_contact": contact,
                "versions": versions,
                "version": version,
                "audit_report": audit_report.model_dump(),
            },
        )


class DataRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_homepage(self, request: Request, repository: Optional[str] = None) -> _TemplateResponse:
        """Retrieves homepage

        Args:
            request:
                The incoming HTTP request.
            repository:
                The repository name.
        """
        registry: CardRegistry = request.app.state.registries.data

        info = list_repository_name_info(registry, repository)
        return templates.TemplateResponse(
            "include/data/data.html",
            {
                "request": request,
                "all_repositories": info.repositories,
                "selected_repository": info.selected_repository,
                "data": info.names,
            },
        )

    def _check_splits(self, card: DataCard) -> Optional[str]:
        if len(card.data_splits) > 0:
            return json.dumps(
                [split.model_dump() for split in card.data_splits],
                indent=4,
            )
        return None

    def _load_profile(
        self, request: Request, load_profile: bool, datacard: DataCard
    ) -> Tuple[Optional[str], bool, bool]:
        """If load_profile is True, attempts to load the data profile

        Args:
            request:
                The incoming HTTP request.
            load_profile:
                Whether to load the data profile.
            datacard:
                The data card.

        Returns:
            `Tuple[str, bool]`
        """
        storage_client = request.app.state.storage_client

        data_html_path = (datacard.uri / SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value)
        html_exists = storage_client.exists(data_html_path)

        if load_profile and html_exists:
            with tempfile.TemporaryDirectory() as tmp_dir:
                lpath = Path(tmp_dir) / data_html_path.name
                storage_client.get(data_html_path, lpath)

                file_size = lpath.stat().st_size
                if file_size / (1024 * 1024) <= 50:
                    with lpath.open("r", encoding="utf-8") as html_file:
                        return html_file.read(), True, html_exists

                else:
                    return "Data profile too large to display. Please download to view.", False, html_exists

        return None, False, html_exists

    def get_versions_page(
        self,
        request: Request,
        name: str,
        load_profile: bool,
        version: Optional[str] = None,
    ) -> _TemplateResponse:
        """Given a data name, returns the data versions page

        Args:
            request:
                The incoming HTTP request.
            name:
                The data name.
            load_profile:
                Whether to load the data profile.
            version:
                The data version.
        """

        registry: CardRegistry = request.app.state.registries.data
        versions = registry.list_cards(name=name, limit=50)

        datacard, version = self._check_version(
            registry,
            name,
            versions,
            version,
            **{"interface": DataInterface},  # generic data interface
        )
        datacard = cast(DataCard, datacard)

        data_splits = self._check_splits(card=datacard)
        data_profile, render_profile, html_exists = self._load_profile(request, load_profile, datacard)

        data_filename = Path(SaveName.DATA.value).with_suffix(datacard.interface.data_suffix)
        data_profile_filename = Path(SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value)

        return templates.TemplateResponse(
            "include/data/data_version.html",
            {
                "request": request,
                "versions": versions,
                "selected_data": datacard,
                "selected_version": version,
                "data_splits": data_splits,
                "data_profile": data_profile,
                "render_profile": render_profile,
                "load_profile": load_profile,
                "html_exists": html_exists,
                "data_filename": data_filename,
                "data_profile_filename": data_profile_filename,
            },
        )


class ModelRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_homepage(self, request: Request, repository: Optional[str] = None) -> _TemplateResponse:
        """Retrieve homepage

        Args:
            request:
                The incoming HTTP request.
            repository:
                The repository name.
        """
        registry: CardRegistry = request.app.state.registries.model

        info = list_repository_name_info(registry, repository)
        return templates.TemplateResponse(
            "include/model/models.html",
            {
                "request": request,
                "all_repositories": info.repositories,
                "selected_repository": info.selected_repository,
                "models": info.names,
            },
        )

    def _get_runcard(self, registry: CardRegistry, modelcard: ModelCard) -> Tuple[Optional[RunCard], Optional[str]]:
        if modelcard.metadata.runcard_uid is not None:
            runcard: RunCard = registry.load_card(uid=modelcard.metadata.runcard_uid)  # type: ignore
            runcard.load_metrics()
            return runcard, runcard.project

        return None, None

    def _get_path(self, name: str, path: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        if path is None:
            return None, None

        rpath = Path(path)

        if rpath.suffix == "":
            save_filename = f"{name}.zip"
        else:
            save_filename = rpath.name

        return rpath.as_posix(), save_filename

    def _get_processor_uris(self, metadata: ModelMetadata) -> Dict[str, Dict[str, Optional[str]]]:
        processor_uris = {}
        dumped_meta = metadata.model_dump()

        # get preprocessor
        rpath, filename = self._get_path("preprocessor", dumped_meta.get("preprocessor_uri"))
        processor_uris["preprocessor"] = {"rpath": rpath, "filename": filename}

        # get tokenizer
        rpath, filename = self._get_path("tokenizer", dumped_meta.get("tokenizer_uri"))
        processor_uris["tokenizer"] = {"rpath": rpath, "filename": filename}

        # get feature extractor
        rpath, filename = self._get_path("feature_extractor", dumped_meta.get("feature_extractor_uri"))
        processor_uris["feature_extractor"] = {"rpath": rpath, "filename": filename}

        return processor_uris

    def get_versions_page(
        self,
        request: Request,
        name: str,
        versions: List[Dict[str, Any]],
        metadata: ModelMetadata,
        version: Optional[str] = None,
    ) -> _TemplateResponse:
        """Given a data name, returns the data versions page

        Args:
            request:
                The incoming HTTP request.
            name:
                The data name.
            versions:
                The list of card versions.
            metadata:
                The model metadata.
            version:
                The data version.
        """

        registry: CardRegistry = request.app.state.registries.model
        modelcard, version = self._check_version(
            registry,
            name,
            versions,
            version,
            **{"interface": ModelInterface},  # model should load generic to avoid import errors
        )

        runcard, project_num = self._get_runcard(
            registry=request.app.state.registries.run,
            modelcard=cast(ModelCard, modelcard),
        )

        metadata_json = json.dumps(metadata.model_dump(), indent=4)

        model_filename = Path(metadata.model_uri)

        if model_filename.suffix == "":
            model_save_filename = "model.zip"
        else:
            model_save_filename = model_filename.name

        onnx_filename = Path(metadata.onnx_uri) if metadata.onnx_uri is not None else None

        if onnx_filename is not None and onnx_filename.suffix == "":
            onnx_save_filename = "onnx.zip"
        elif onnx_filename is not None:
            onnx_save_filename = onnx_filename.name
        else:
            onnx_save_filename = None

        processor_uris = self._get_processor_uris(metadata)

        return templates.TemplateResponse(
            "include/model/model_version.html",
            {
                "request": request,
                "versions": versions,
                "selected_model": modelcard,
                "selected_version": version,
                "project_num": project_num,
                "metadata": metadata,
                "runcard": runcard,
                "metadata_json": metadata_json,
                "model_filename": model_save_filename,
                "processor_uris": processor_uris,
                "onnx_filename": onnx_save_filename,
            },
        )


class ProjectRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_run_metrics(self, request: Request, run_uid: str) -> _TemplateResponse:
        """Retrieve homepage

        Args:
            request:
                The incoming HTTP request.
            run_uid:
                The run uid.
        """
        run_registry: CardRegistry = request.app.state.registries.run
        runcard: RunCard = run_registry.load_card(uid=run_uid)

        # load metrics from sql db
        runcard.load_metrics()

        return templates.TemplateResponse(
            "include/project/metric_page.html",
            {
                "request": request,
                "runcard": runcard.model_dump(),
            },
        )

    def get_unique_projects(self, project_registry: CardRegistry) -> List[str]:
        """Get unique projects

        Args:
            project_registry:
                The project registry.
        """

        projects = project_registry.list_cards(limit=1000)

        return sorted(list(set(project["name"] for project in projects)))

    def load_graphs(self, runcard: RunCard) -> Dict[str, Any]:
        """Load graphs from runcard

        Args:
            runcard:
                The run card.
        """
        loaded_graphs: Dict[str, Any] = {}
        graph_path = runcard.uri / SaveName.GRAPHS.value
        path_exists = client.storage_client.exists(graph_path)

        # skip if path does not exist
        if not path_exists:
            return loaded_graphs

        paths = client.storage_client.ls(graph_path)
        logger.debug("Found {} graphs in {}", paths, graph_path)
        if paths:
            with tempfile.TemporaryDirectory() as tmp_dir:
                for path in paths:
                    rpath = graph_path / Path(path).name
                    lpath = Path(tmp_dir) / rpath.name
                    client.storage_client.get(rpath, lpath)
                    graph: Dict[str, Any] = joblib.load(lpath)
                    loaded_graphs[graph["name"]] = graph

        return loaded_graphs

    def get_project_runs(self, project: str, run_registry: CardRegistry) -> List[Dict[str, Any]]:
        """Get runs for a project

        Args:
            project:
                The selected project.
            run_registry:
                The run registry.
        """
        project_runs = run_registry._registry.list_cards(
            limit=100,
            query_terms={"project": project},
        )

        return sorted(project_runs, key=lambda k: k["timestamp"], reverse=True)

    def get_project_run(
        self,
        request: Request,
        project: Optional[str] = None,
        run_uid: Optional[str] = None,
    ) -> _TemplateResponse:
        """Retrieve homepage

        Args:
            request:
                The incoming HTTP request.
            project:
                The project name.
            run_uid:
                The run uid.
        """
        project_registry: CardRegistry = request.app.state.registries.project
        run_registry: CardRegistry = request.app.state.registries.run

        unique_projects = self.get_unique_projects(project_registry)

        logger.debug(f"unique_projects: {unique_projects}")

        if len(unique_projects) == 0:
            return templates.TemplateResponse(
                "include/project/no_projects.html",
                {"request": request},
            )

        if project is None:
            selected_project = unique_projects[0]
        else:
            selected_project = project

        # get projects
        project_runs = self.get_project_runs(selected_project, run_registry)

        logger.debug("Found {} runs", len(project_runs))

        if run_uid is not None:
            runcard: RunCard = run_registry.load_card(uid=run_uid)
        else:
            if len(project_runs) == 0:
                return templates.TemplateResponse(
                    "include/project/projects.html",
                    {
                        "request": request,
                        "all_projects": unique_projects,
                        "selected_project": selected_project,
                        "project_runs": project_runs,
                    },
                )

            runcard: RunCard = run_registry.load_card(uid=project_runs[0]["uid"])  # type: ignore[no-redef]

        # load metrics from db
        runcard.load_metrics()

        return templates.TemplateResponse(
            "include/project/projects.html",
            {
                "request": request,
                "all_projects": unique_projects,
                "selected_project": selected_project,
                "project_runs": project_runs,
                "runcard": runcard,
                "graphs": self.load_graphs(runcard),
            },
        )
