# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import codecs
import csv
import datetime
import os
from typing import Any, BinaryIO, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from opsml.app.routes.pydantic_models import (
    AuditFormRequest,
    AuditReport,
    CommentSaveRequest,
)
from opsml.app.routes.route_helpers import AuditRouteHelper
from opsml.app.routes.utils import (
    AuditFormParser,
    error_to_500,
    get_names_teams_versions,
    write_records_to_csv,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import AuditCard
from opsml.registry.cards.audit import AuditSections

logger = ArtifactLogger.get_logger()

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
AUDIT_FILE = "audit_file.csv"

templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()
audit_route_helper = AuditRouteHelper()


@router.get("/audit/", response_class=HTMLResponse)
@error_to_500
async def audit_list_homepage(
    request: Request,
    team: Optional[str] = None,
    model: Optional[str] = None,
    email: Optional[str] = None,
    version: Optional[str] = None,
    uid: Optional[str] = None,
):
    """UI home for listing models in model registry

    Args:
        request:
            The incoming HTTP request.
        team:
            Team name
        model:
            Model name
        email:
            User email
        version:
            Model version
        uid:
            AuditCard uid
    Returns:
        200 if the request is successful. The body will contain a JSON string
        with the list of models.
    """

    if all(attr is None for attr in [uid, version, model, team]):
        return audit_route_helper.get_homepage(request=request)

    if team is not None and all(attr is None for attr in [version, model]):
        return audit_route_helper.get_team_page(request=request, team=team)

    if team is not None and model is not None and version is None:
        return audit_route_helper.get_versions_page(request=request, team=team, name=model)

    if model is not None and team is not None and all(attr is None for attr in [uid, version]):
        raise ValueError("Model name provided without either version or uid")

    return audit_route_helper.get_name_version_page(
        request=request,
        team=str(team),
        name=str(model),
        email=email,
        version=version,
        uid=uid,
    )


@router.post("/audit/save", response_class=HTMLResponse)
@error_to_500
async def save_audit_form(
    request: Request,
    form: AuditFormRequest = Depends(AuditFormRequest),
):
    # collect all function arguments into a dictionary

    # base attr needed for html
    model_names, teams, versions = get_names_teams_versions(
        registry=request.app.state.registries.model,
        name=form.selected_model_name,
        team=form.selected_model_team,
    )

    parser = AuditFormParser(
        audit_form_dict=form.model_dump(),
        registries=request.app.state.registries,
    )
    audit_card = parser.parse_form()

    audit_report = AuditReport(
        name=audit_card.name,
        team=audit_card.team,
        user_email=audit_card.user_email,
        version=audit_card.version,
        uid=audit_card.uid,
        status=audit_card.approved,
        audit=audit_card.audit.model_dump(),  # using updated section
        timestamp=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")),
        comments=audit_card.comments,
    )

    return templates.TemplateResponse(
        "include/audit/audit.html",
        {
            "request": request,
            "teams": teams,
            "selected_team": form.selected_model_team,
            "models": model_names,
            "selected_model": form.selected_model_name,
            "selected_email": form.selected_model_email,
            "versions": versions,
            "version": form.selected_model_version,
            "audit_report": audit_report.model_dump(),
        },
    )


@router.post("/audit/comment/save", response_class=HTMLResponse)
@error_to_500
async def save_audit_comment(
    request: Request,
    comment: CommentSaveRequest = Depends(CommentSaveRequest),
):
    """Save comment to AuditCard

    Args:
        request:
            The incoming HTTP request.
        comment:
            `CommentSaveRequest`
    """

    audit_card: AuditCard = request.app.state.registries.audit.load_card(uid=comment.uid)

    # most recent first
    audit_card.add_comment(
        name=comment.comment_name,
        comment=comment.comment_text,
    )
    model_names, teams, versions = get_names_teams_versions(
        registry=request.app.state.registries.model,
        name=comment.selected_model_name,
        team=comment.selected_model_team,
    )

    request.app.state.registries.audit.update_card(card=audit_card)

    audit_report = AuditReport(
        name=audit_card.name,
        team=audit_card.team,
        user_email=audit_card.user_email,
        version=audit_card.version,
        uid=audit_card.uid,
        status=audit_card.approved,
        audit=audit_card.audit.model_dump(),  # using updated section
        timestamp=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")),
        comments=audit_card.comments,
    )

    return templates.TemplateResponse(
        "include/audit/audit.html",
        {
            "request": request,
            "teams": teams,
            "selected_team": comment.selected_model_team,
            "models": model_names,
            "selected_model": comment.selected_model_name,
            "selected_email": comment.selected_model_email,
            "versions": versions,
            "version": comment.selected_model_version,
            "audit_report": audit_report.model_dump(),
        },
    )


class AuditFormUploader:
    def __init__(self, form: AuditFormRequest, background_tasks: BackgroundTasks):
        self.form = form
        self.background_tasks = background_tasks

    @property
    def audit_file(self) -> BinaryIO:
        if self.form.audit_file is None:
            raise ValueError("No audit file provided")
        return self.form.audit_file.file

    def read_file(self) -> List[Dict[str, Any]]:
        """Reads an audit file to dictionary"""

        csv_reader = csv.DictReader(codecs.iterdecode(self.audit_file, "utf-8"))
        self.background_tasks.add_task(self.audit_file.close)
        records = list(csv_reader)
        return records

    def upload_audit(self) -> Dict[str, Any]:
        """Uploads audit data from file to AuditCard"""
        audit_sections = AuditSections().model_dump()  # type:ignore
        records = self.read_file()
        for record in records:
            section = record["topic"]
            number = int(record["number"])
            audit_sections[section][number]["response"] = record["response"]
        return audit_sections


@router.post("/audit/upload", response_class=HTMLResponse)
@error_to_500
async def upload_audit_data(
    request: Request,
    background_tasks: BackgroundTasks,
    form: AuditFormRequest = Depends(AuditFormRequest),
):
    """Uploads audit data form file. If an audit_uid is provided, only the audit section will be updated."""
    uploader = AuditFormUploader(
        form=form,
        background_tasks=background_tasks,
    )
    audit_sections = uploader.upload_audit()

    if form.uid is not None:
        audit_card: AuditCard = request.app.state.registries.audit.load_card(uid=form.uid)
        audit_report = AuditReport(
            name=audit_card.name,
            team=audit_card.team,
            user_email=audit_card.user_email,
            version=audit_card.version,
            uid=audit_card.uid,
            status=audit_card.approved,
            audit=audit_sections,  # using updated section
            timestamp=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")),
            comments=audit_card.comments,
        )

    else:
        audit_report = AuditReport(
            name=form.name or form.selected_model_name,
            team=form.team or form.selected_model_team,
            user_email=form.email or form.selected_model_email,
            version=form.version,
            uid=form.uid,
            status=form.status,
            audit=audit_sections,  # using updated section
            timestamp=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")),
            comments=[],
        )

    # base attr needed for html
    model_names, teams, versions = get_names_teams_versions(
        registry=request.app.state.registries.model,
        name=form.selected_model_name,
        team=form.selected_model_team,
    )

    return templates.TemplateResponse(
        "include/audit/audit.html",
        {
            "request": request,
            "teams": teams,
            "selected_team": form.selected_model_team,
            "models": model_names,
            "selected_model": form.selected_model_name,
            "selected_email": form.selected_model_name,
            "versions": versions,
            "version": form.selected_model_version,
            "audit_report": audit_report.model_dump(),
        },
    )


@router.post("/audit/download", response_class=StreamingResponse)
@error_to_500
async def download_audit_data(
    request: Request,
    form: AuditFormRequest = Depends(AuditFormRequest),
) -> StreamingResponse:
    """Downloads Audit Form data to csv"""

    field_names = ["topic", "number", "question", "purpose", "response"]

    parser = AuditFormParser(
        audit_form_dict=form.model_dump(),
        registries=request.app.state.registries,
    )
    audit_card = parser.parse_form()

    # unnest audit section into list of dicts and save to csv
    audit_section = audit_card.audit.model_dump()
    audit_records = []

    for section, questions in audit_section.items():
        for question_nbr, question in questions.items():
            audit_records.append(
                {
                    "topic": section,
                    "number": question_nbr,
                    "question": question["question"],
                    "purpose": question["purpose"],
                    "response": question["response"],
                }
            )

    response = write_records_to_csv(
        records=audit_records,
        field_names=field_names,
    )

    return response
