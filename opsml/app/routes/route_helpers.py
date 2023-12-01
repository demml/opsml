# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple, cast

from fastapi import Request
from fastapi.templating import Jinja2Templates

from opsml.app.routes.pydantic_models import AuditReport
from opsml.app.routes.utils import get_names_teams_versions, list_team_name_info
from opsml.model.types import ModelMetadata
from opsml.projects import OpsmlProject, ProjectInfo
from opsml.registry import AuditCard, CardRegistry, DataCard, RunCard
from opsml.registry.cards import ArtifactCard, ModelCard
from opsml.registry.cards.audit import AuditSections
from opsml.registry.utils.settings import settings
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
templates = Jinja2Templates(directory=TEMPLATE_PATH)


class RouteHelper:
    def _check_version(
        self,
        registry: CardRegistry,
        name: str,
        versions: List[Dict[str, Any]],
        version: Optional[str] = None,
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
            selected_card = registry.load_card(uid=versions[0]["uid"])
            version = selected_card.version

            return selected_card, str(version)

        return registry.load_card(name=name, version=version), version


class AuditRouteHelper(RouteHelper):
    """Route helper for AuditCard pages"""

    def get_homepage(self, request: Request):
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
                "teams": request.app.state.registries.model._registry.unique_teams,
                "models": None,
                "selected_team": None,
                "selected_model": None,
                "version": None,
                "audit_report": None,
            },
        )

    def get_team_page(self, request: Request, team: str):
        """Returns audit page for a specific team

        Args:
            request:
                The incoming HTTP request.
            team:
                The team name.
        """
        teams = request.app.state.registries.model._registry.unique_teams
        model_names = request.app.state.registries.model._registry.get_unique_card_names(team=team)
        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "teams": teams,
                "selected_team": team,
                "models": model_names,
                "versions": None,
                "selected_model": None,
                "version": None,
                "audit_report": None,
            },
        )

    def get_versions_page(self, request: Request, name: str, team: str):
        """Returns the audit page for a model name, team, and versions

        Args:
            request:
                The incoming HTTP request.
            name:
                The model name.
            team:
                The team name.
        """
        model_names, teams, versions = get_names_teams_versions(
            registry=request.app.state.registries.model,
            name=name,
            team=team,
        )

        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "teams": teams,
                "selected_team": team,
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
                team=None,
                user_email=None,
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
            team=audit_card.team,
            user_email=audit_card.user_email,
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
        team: str,
        name: str,
        version: Optional[str] = None,
        email: Optional[str] = None,
        uid: Optional[str] = None,
    ):
        """Get audit information for model version

        Args:
            request:
                The incoming HTTP request.
            team:
                The team name.
            name:
                The model name.
            version:
                The model version.
            uid:
                The model uid.
            email:
                The user email.
        """

        model_names, teams, versions = get_names_teams_versions(
            registry=request.app.state.registries.model,
            name=name,
            team=team,
        )

        model_record = request.app.state.registries.model.list_cards(
            name=name,
            version=version,
            uid=uid,
        )[0]

        email = model_record.get("user_email") if email is None else email

        audit_report = self._get_audit_report(
            audit_registry=request.app.state.registries.audit,
            uid=model_record.get("auditcard_uid"),
        )

        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "teams": teams,
                "selected_team": team,
                "models": model_names,
                "selected_model": name,
                "selected_email": email,
                "versions": versions,
                "version": version,
                "audit_report": audit_report.model_dump(),
            },
        )


class DataRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_homepage(self, request: Request, team: Optional[str] = None):
        """Retrieves homepage

        Args:
            request:
                The incoming HTTP request.
            team:
                The team name.
        """
        registry: CardRegistry = request.app.state.registries.data

        info = list_team_name_info(registry, team)
        return templates.TemplateResponse(
            "include/data/data.html",
            {
                "request": request,
                "all_teams": info.teams,
                "selected_team": info.selected_team,
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

    def _load_profile(self, request: Request, load_profile: bool, datacard: DataCard) -> Tuple[Optional[str], bool]:
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
        if load_profile and datacard.metadata.uris.profile_html_uri is not None:
            with tempfile.TemporaryDirectory() as tmp_dir:
                filepath = request.app.state.storage_client.download(
                    datacard.metadata.uris.profile_html_uri,
                    tmp_dir,
                )

                stats = os.stat(filepath)
                if stats.st_size / (1024 * 1024) <= 50:
                    with open(filepath, "r", encoding="utf-8") as html_file:
                        return html_file.read(), True
                else:
                    return "Data profile too large to display. Please download to view.", False

        return None, False

    def get_versions_page(
        self,
        request: Request,
        name: str,
        load_profile: bool,
        version: Optional[str] = None,
    ):
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
        versions = registry.list_cards(name=name, as_dataframe=False, limit=50)
        datacard, version = self._check_version(registry, name, versions, version)
        datacard = cast(DataCard, datacard)

        data_splits = self._check_splits(card=datacard)
        data_profile, render_profile = self._load_profile(request, load_profile, datacard)

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
            },
        )

    def get_data_profile_page(
        self,
        request: Request,
        name: str,
        version: str,
        profile_uri: Optional[str] = None,
    ):
        """Loads the data profile page

        Args:
            request:
                The incoming HTTP request.
            name:
                The data name.
            version:
                The data version.
            profile_uri:
                The data profile uri.
        """
        if profile_uri is None:
            data_profile = "No profile found"
            render = False
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                filepath = request.app.state.storage_client.download(profile_uri, tmp_dir)
                stats = os.stat(filepath)
                if stats.st_size / (1024 * 1024) <= 50:
                    with open(filepath, "r", encoding="utf-8") as html_file:
                        data_profile = html_file.read()
                        render = True

                else:
                    data_profile = "Data profile too large to display. Please download to view."
                    render = False

        return templates.TemplateResponse(
            "include/data/data_profile.html",
            {
                "request": request,
                "name": name,
                "data_profile": data_profile,
                "version": version,
                "render": render,
            },
        )


class ModelRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_homepage(self, request: Request, team: Optional[str] = None):
        """Retrieve homepage

        Args:
            request:
                The incoming HTTP request.
            team:
                The team name.
        """
        registry: CardRegistry = request.app.state.registries.model

        info = list_team_name_info(registry, team)
        return templates.TemplateResponse(
            "include/model/models.html",
            {
                "request": request,
                "all_teams": info.teams,
                "selected_team": info.selected_team,
                "models": info.names,
            },
        )

    def _get_runcard(
        self,
        request: Request,
        registry: CardRegistry,
        modelcard: ModelCard,
    ) -> Tuple[Optional[RunCard], Optional[str]]:
        if modelcard.metadata.runcard_uid is not None:
            runcard: RunCard = registry.load_card(uid=modelcard.metadata.runcard_uid)  # type: ignore
            project_num = request.app.state.mlflow_client.get_experiment_by_name(name=runcard.project_id).experiment_id

            return runcard, project_num

        return None, None

    def _check_data_dim(self, metadata: ModelMetadata) -> Tuple[str, str]:
        """Checks if the data dimension is too large to load in the UI

        Args:
            metadata:
                The model metadata.

        Returns:
            `Tuple[str, str]`
        """
        max_dim = 0
        if metadata.data_schema.model_data_schema.data_type == "NUMPY_ARRAY":
            features = metadata.data_schema.model_data_schema.input_features
            inputs = features.get("inputs")
            if inputs is not None:
                max_dim = max(inputs.shape)
        # capping amount of sample data shown

        if max_dim > 200:
            metadata.sample_data = {"inputs": "Sample data is too large to load in ui"}

        metadata_json = json.dumps(metadata.model_dump(), indent=4)
        sample_data = json.dumps(metadata.sample_data, indent=4)

        return metadata_json, sample_data

    def get_versions_page(
        self,
        request: Request,
        name: str,
        versions: List[Dict[str, Any]],
        metadata: ModelMetadata,
        version: Optional[str] = None,
    ):
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
        modelcard, version = self._check_version(registry, name, versions, version)

        runcard, project_num = self._get_runcard(
            request=request,
            registry=request.app.state.registries.run,
            modelcard=cast(ModelCard, modelcard),
        )

        metadata_json, sample_data = self._check_data_dim(metadata)

        return templates.TemplateResponse(
            "include/model/model_version.html",
            {
                "request": request,
                "versions": versions,
                "selected_model": modelcard,
                "selected_version": version,
                "project_num": project_num,
                "metadata": metadata,
                "sample_data": sample_data,
                "runcard": runcard,
                "metadata_json": metadata_json,
            },
        )


class ProjectRouteHelper(RouteHelper):
    """Route helper for DataCard pages"""

    def get_run_metrics(self, request: Request, run_uid: str):
        """Retrieve homepage

        Args:
            request:
                The incoming HTTP request.
            run_uid:
                The run uid.
        """
        run_registry: CardRegistry = request.app.state.registries.run
        runcard = run_registry.load_card(uid=run_uid).model_dump()

        return templates.TemplateResponse(
            "include/project/metric_page.html",
            {
                "request": request,
                "runcard": runcard,
            },
        )

    def get_unique_projects(self, project_registry: CardRegistry) -> List[str]:
        """Get unique projects

        Args:
            project_registry:
                The project registry.
        """

        projects = project_registry.list_cards()
        return list(set(f"{project['team']}:{project['name']}" for project in projects))

    def get_project_runs(self, selected_project: str) -> List[Dict[str, Any]]:
        """Get runs for a project

        Args:
            selected_project:
                The selected project.
        """
        # get projects
        project_info = ProjectInfo(
            name=selected_project.split(":")[1],
            team=selected_project.split(":")[0],
        )
        project = OpsmlProject(project_info)
        return project.list_runs()

    def remove_old_mlflow_path(self, runcard: RunCard) -> RunCard:
        """Method use to remove old mlflow paths

        Args:
            runcard:
                The run card.

        Returns:
            `RunCard`
        """

        for key, val in runcard.artifact_uris.items():
            new_val = val.replace("mlflow-artifacts:", settings.storage_settings.storage_uri)
            runcard.artifact_uris[key] = new_val
        return runcard

    def get_project_run(
        self,
        request: Request,
        project: Optional[str] = None,
        run_uid: Optional[str] = None,
    ):
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

        logger.info(f"unique_projects: {unique_projects}")

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
        project_runs = self.get_project_runs(selected_project)

        if run_uid is not None:
            runcard = run_registry.load_card(uid=run_uid)
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
            runcard = run_registry.load_card(uid=project_runs[0]["uid"])

        runcard = self.remove_old_mlflow_path(
            runcard=cast(RunCard, runcard),
        )

        return templates.TemplateResponse(
            "include/project/projects.html",
            {
                "request": request,
                "all_projects": unique_projects,
                "selected_project": selected_project,
                "project_runs": project_runs,
                "runcard": runcard,
            },
        )
