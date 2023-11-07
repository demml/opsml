import os
from typing import Optional, cast, List, Dict, Any, Tuple
from fastapi import Request
import json
import tempfile
from fastapi.templating import Jinja2Templates
from opsml.model.types import ModelMetadata
from opsml.registry.cards import ArtifactCard, ModelCard
from opsml.registry import CardRegistry, AuditCard, DataCard, RunCard
from opsml.app.routes.utils import get_names_teams_versions, list_team_name_info
from opsml.app.routes.pydantic_models import AuditReport
from opsml.registry.cards.audit import AuditSections

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
templates = Jinja2Templates(directory=TEMPLATE_PATH)


class RouteHelper:
    def get_homepage(self, request: Request, **kwargs) -> Jinja2Templates.TemplateResponse:
        raise NotImplementedError

    def get_team_page(self, request: Request, team: str) -> Jinja2Templates.TemplateResponse:
        raise NotImplementedError

    def get_versions_page(self, request: Request, name: str, **kwargs) -> Jinja2Templates.TemplateResponse:
        raise NotImplementedError

    def get_name_version_page(
        self,
        request: Request,
        team: str,
        name: str,
        version: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> Jinja2Templates.TemplateResponse:
        raise NotImplementedError

    def _check_version(
        self,
        registry: CardRegistry,
        name: str,
        versions: List[Dict[str, Any]],
        version: Optional[str] = None,
    ) -> Tuple[ArtifactCard, str]:
        if version is None:
            selected_card = registry.load_card(uid=versions[0]["uid"])
            version = selected_card.version

            return selected_card, version

        return registry.load_card(name=name, version=version), version


class AuditRouteHelper(RouteHelper):
    """Route helper for AuditCard pages"""

    def get_homepage(request: Request, **kwargs) -> Jinja2Templates.TemplateResponse:
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

    def get_team_page(self, request: Request, team: str) -> Jinja2Templates.TemplateResponse:
        """Returns audit page for a specific team"""
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

    def get_version_page(self, request: Request, name: str, **kwargs) -> Jinja2Templates.TemplateResponse:
        """Returns the audit page for a model name, team, and versions"""
        team = cast(str, kwargs.get("team"))
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

        audit_card: AuditCard = audit_registry.load_card(uid=uid)
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
        uid: Optional[str] = None,
    ) -> Jinja2Templates.TemplateResponse:
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

    def get_homepage(self, request: Request, **kwargs) -> Jinja2Templates.TemplateResponse:
        registry: CardRegistry = request.app.state.registries.data
        team = kwargs.get("team")

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
        if load_profile:
            if datacard.metadata.uris.profile_html_uri is not None:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    filepath = request.app.state.storage_client.download(
                        datacard.metadata.uris.profile_html_uri, tmp_dir
                    )

                stats = os.stat(filepath)
                if stats.st_size / (1024 * 1024) <= 50:
                    with open(filepath, "r", encoding="utf-8") as html_file:
                        return html_file.read(), True
                else:
                    return "Data profile too large to display. Please download to view.", False

        return None, False

    def get_versions_page(self, request: Request, name: str, **kwargs) -> Jinja2Templates.TemplateResponse:
        """Given a data name, returns the data versions page"""
        version = kwargs.get("version")
        load_profile = kwargs.get("load_profile")

        registry: CardRegistry = request.app.state.registries.data
        versions = registry.list_cards(name=name, as_dataframe=False, limit=50)
        datacard, version = self._check_version(registry, name, versions, version)

        data_splits = self._check_splits(datacard)
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
    ) -> Jinja2Templates.TemplateResponse:
        """Loads the data profile page"""
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

    def get_homepage(self, request: Request, **kwargs) -> Jinja2Templates.TemplateResponse:
        registry: CardRegistry = request.app.state.registries.model
        team = kwargs.get("team")

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
        self, request: Request, registry: CardRegistry, modelcard: ModelCard
    ) -> Tuple[Optional[RunCard], Optional[str]]:
        if modelcard.metadata.runcard_uid is not None:
            runcard = registry.load_card(uid=modelcard.metadata.runcard_uid)
            project_num = request.app.state.mlflow_client.get_experiment_by_name(name=runcard.project_id).experiment_id

            return runcard, project_num

        return None, None

    def _check_data_dim(self, metadata: ModelMetadata) -> Tuple[str, str]:
        """Checks if the data dimension is too large to load in the UI"""
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

    def get_versions_page(self, request: Request, name: str, **kwargs) -> Jinja2Templates.TemplateResponse:
        """Given a data name, returns the data versions page"""
        version = kwargs.get("version")
        versions = cast(List[Dict[str, Any]], kwargs.get("versions"))
        metadata = cast(ModelMetadata, kwargs.get("metadata"))

        registry: CardRegistry = request.app.state.registries.model

        modelcard, version = self._check_version(registry, name, versions, version)
        runcard, project_num = self._get_runcard(
            request=request,
            registry=registry,
            modelcard=modelcard,
        )

        metadata_json, sample_data = self._check_data_dim(metadata)

        return templates.TemplateResponse(
            "include/model/model_version.html",
            {
                "request": request,
                "versions": versions,
                "selected_model": name,
                "selected_version": version,
                "project_num": project_num,
                "metadata": metadata,
                "sample_data": sample_data,
                "runcard": runcard,
                "metadata_json": metadata_json,
            },
        )
