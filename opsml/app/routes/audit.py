# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import codecs
import csv
import datetime
import io
import os
import re
from typing import Any, BinaryIO, Dict, List, Optional, Union

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from opsml.app.routes.pydantic_models import (
    AuditFormRequest,
    AuditReport,
    CommentSaveRequest,
)
from opsml.app.routes.utils import error_to_500, get_names_teams_versions
from opsml.helpers.logging import ArtifactLogger
from opsml.registry import AuditCard, CardRegistries
from opsml.registry.cards.audit import AuditSections

logger = ArtifactLogger.get_logger()

# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))
AUDIT_FILE = "audit_file.csv"

templates = Jinja2Templates(directory=TEMPLATE_PATH)

router = APIRouter()


@router.get("/audit/")
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

    if team is not None and all(attr is None for attr in [version, model]):
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

    if team is not None and model is not None and version is None:
        model_names, teams, versions = get_names_teams_versions(
            registry=request.app.state.registries.model,
            name=model,
            team=team,
        )

        return templates.TemplateResponse(
            "include/audit/audit.html",
            {
                "request": request,
                "teams": teams,
                "selected_team": team,
                "models": model_names,
                "selected_model": model,
                "versions": versions,
                "version": None,
                "audit_report": None,
            },
        )

    model_names, teams, versions = get_names_teams_versions(
        registry=request.app.state.registries.model,
        name=str(model),
        team=str(team),
    )
    model_record = request.app.state.registries.model.list_cards(
        name=model,
        version=version,
        uid=uid,
    )[0]

    email = model_record.get("user_email") if email is None else email

    auditcard_uid = model_record.get("auditcard_uid")

    if auditcard_uid is None:
        audit_report = AuditReport(
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

    else:
        audit_card: AuditCard = request.app.state.registries.audit.load_card(uid=auditcard_uid)

        audit_report = AuditReport(
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

    return templates.TemplateResponse(
        "include/audit/audit.html",
        {
            "request": request,
            "teams": teams,
            "selected_team": team,
            "models": model_names,
            "selected_model": model,
            "selected_email": email,
            "versions": versions,
            "version": version,
            "audit_report": audit_report.model_dump(),
        },
    )


class AuditFormParser:
    def __init__(self, audit_form_dict: Dict[str, str], registries: CardRegistries):
        """Instantiates parse for audit form data

        Args:
            audit_dict:
                Dictionary of audit form data
            registries:
                `CardRegistries`
        """
        self.audit_form_dict = audit_form_dict
        self.registries = registries

    def _add_auditcard_to_modelcard(self, auditcard_uid: str) -> None:
        """Adds registered AuditCard uid to ModelCard

        Args:
            auditcard_uid:
                AuditCard uid to add to ModelCard
        """
        model_record = self.registries.model.list_cards(
            name=self.audit_form_dict["selected_model_name"],
            version=self.audit_form_dict["selected_model_version"],
        )[0]

        model_record["auditcard_uid"] = auditcard_uid
        self.registries.model._registry.update_card_record(card=model_record)

    def register_update_audit_card(self, audit_card: AuditCard) -> None:
        """Register or update an AuditCard. This will always use server-side registration,
        as the auditcard_uid is created/updated via form data

        Args:
            audit_card:
                `AuditCard`

        Returns:
            None
        """
        # register/update audit
        if audit_card.uid is not None:
            return self.registries.audit.update_card(card=audit_card)
        self.registries.audit.register_card(card=audit_card)
        self._add_auditcard_to_modelcard(auditcard_uid=audit_card.uid)
        return None

    def get_audit_card(self) -> AuditCard:
        """Gets or creates AuditCard to use with Form data

        Returns:
            `AuditCard`
        """
        if self.audit_form_dict["uid"] is not None:
            # check first
            records = self.registries.audit.list_cards(uid=self.audit_form_dict["uid"])

            if bool(records):
                audit_card: AuditCard = self.registries.audit.load_card(uid=self.audit_form_dict["uid"])

            else:
                logger.info("Invalid uid specified, defaulting to new AuditCard")
                audit_card = AuditCard(
                    name=self.audit_form_dict["name"],
                    team=self.audit_form_dict["team"],
                    user_email=self.audit_form_dict["email"],
                )
        else:
            audit_card = AuditCard(
                name=self.audit_form_dict["name"],
                team=self.audit_form_dict["team"],
                user_email=self.audit_form_dict["email"],
            )

        return audit_card

    def parse_form_sections(self, audit_card: AuditCard) -> AuditCard:
        """Parses form data into AuditCard

        Args:
            audit_card:
                `AuditCard`

        Returns:
            `AuditCard`
        """
        audit_section = audit_card.audit.model_dump()
        for question_key, response in self.audit_form_dict.items():
            if bool(re.search(r"\d", question_key)) and response is not None:
                splits = question_key.split("_")
                section = "_".join(splits[:-1])
                number = int(splits[-1])  # this will always be an int
                audit_section[section][number]["response"] = response

        # recreate section
        audit_card.audit = AuditSections(**audit_section)
        return audit_card

    def parse_form(self) -> AuditCard:
        """Parses form data into AuditCard"""

        audit_card = self.get_audit_card()
        audit_card = self.parse_form_sections(audit_card=audit_card)
        self.register_update_audit_card(audit_card=audit_card)

        return audit_card


@router.post("/audit/save")
@error_to_500
async def save_audit_form(request: Request, form: AuditFormRequest = Depends(AuditFormRequest)):
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


@router.post("/audit/comment/save")
@error_to_500
async def save_audit_comment(request: Request, comment: CommentSaveRequest = Depends(CommentSaveRequest)):
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


@router.post("/audit/upload")
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


def write_audit_to_csv(
    audit_records: List[Dict[str, Optional[Union[str, int]]]],
    field_names: List[str],
) -> StreamingResponse:
    """Writes audit data to csv and returns FileResponse

    Args:
        audit_records:
            List of audit records
        field_names:
            List of field names for csv header

    Returns:
        FileResponse
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(audit_records)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "filename=audit_file.csv"},
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

    response = write_audit_to_csv(
        audit_records=audit_records,
        field_names=field_names,
    )

    return response
