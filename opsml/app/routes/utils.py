# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import csv
import io
import os
import re
import traceback
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from streaming_form_data.targets import FileTarget

from opsml.app.routes.pydantic_models import ListTeamNameInfo
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.audit import AuditCard, AuditSections
from opsml.registry.cards.run import RunCard
from opsml.registry.cards.types import RegistryType
from opsml.registry.sql.registry import CardRegistries, CardRegistry
from opsml.registry.storage.storage_system import LocalStorageClient, StorageClientType

logger = ArtifactLogger.get_logger()
# Constants
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_PATH = os.path.abspath(os.path.join(PARENT_DIR, "templates"))


templates = Jinja2Templates(directory=TEMPLATE_PATH)


def get_model_versions(registry: CardRegistry, model: str, team: str) -> List[str]:
    """Returns a list of model versions for a given team and model

    Args:
        registry:
            The registry to query
        model:
            The model to query
        team:
            The team to query
    Returns:
        A list of model versions
    """

    return [card["version"] for card in registry.list_cards(name=model, team=team, as_dataframe=False)]


def get_names_teams_versions(registry: CardRegistry, team: str, name: str) -> Tuple[List[str], List[str], List[str]]:
    """Helper functions to get the names, teams, and versions for a given registry

    Args:
        registry:
            The registry to query
        team:
            The team to query
        name:
            The name to query
    Returns:
        A tuple of names, teams, and versions
    """

    teams = registry._registry.unique_teams  # pylint: disable=protected-access
    versions = get_model_versions(registry, name, team)
    names = registry._registry.get_unique_card_names(team=team)  # pylint: disable=protected-access
    return names, teams, versions


def get_runcard_from_model(
    registries: CardRegistries,
    name: Optional[str] = None,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> Optional[RunCard]:
    """Loads the runcard associated with a modelcard

    Args:
        registries:
            CardRegistries object
        name:
            Name of the model
        version:
            Version of the model
        uid:
            UID of the model
    Returns:
        RunCard object
    """
    modelcard = registries.model.list_cards(
        name=name,
        version=version,
        uid=uid,
    )[0]

    run_uid = modelcard.get("runcard_uid", None)

    if run_uid is not None:
        return cast(RunCard, registries.run.load_card(uid=run_uid))

    return None


def error_to_500(func: Callable[..., Any]) -> Any:
    """Function for wrapping errors in the opsml UI"""

    @wraps(func)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
        try:
            return await func(request, *args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            trace_back = traceback.format_exc()
            logger.error("exceptions: {} {}", exc, trace_back)
            return templates.TemplateResponse(
                "include/500.html",
                {
                    "request": request,
                    "error_message": str(exc),
                },
            )

    return wrapper


def get_registry_type_from_table(
    table_name: Optional[str] = None,
    registry_type: Optional[str] = None,
) -> str:
    """
    This is a hack to get the registry type from the table name.
    This is needed to maintain backwards compatibility in V1
    """

    if table_name is not None:
        for _registry_type in RegistryType:
            if _registry_type.value.upper() in table_name:
                return _registry_type.value

    if registry_type is not None:
        return registry_type

    raise ValueError("Could not determine registry type")


def get_real_path(current_path: str, proxy_root: str, storage_root: str) -> str:
    new_path = current_path.replace(proxy_root, f"{storage_root}/")
    return new_path


def replace_proxy_root(
    card: Dict[str, Any],
    storage_root: str,
    proxy_root: str,
) -> Dict[str, Any]:
    for name, value in card.items():
        if "uri" in name:
            if isinstance(value, str):
                real_path = get_real_path(
                    current_path=value,
                    proxy_root=proxy_root,
                    storage_root=storage_root,
                )
                card[name] = real_path

        if isinstance(value, dict):
            replace_proxy_root(
                card=value,
                storage_root=storage_root,
                proxy_root=proxy_root,
            )

    return card


class MaxBodySizeException(Exception):
    def __init__(self, body_len: int):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes) -> None:
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


class ExternalFileTarget(FileTarget):  # type: ignore[misc]
    def __init__(  # pylint: disable=keyword-arg-before-vararg
        self,
        filename: str,
        write_path: str,
        storage_client: StorageClientType,
        allow_overwrite: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(filename=filename, allow_overwrite=allow_overwrite, *args, **kwargs)

        self.storage_client = storage_client
        self.write_path = write_path
        self.filepath = f"{self.write_path}/{filename}"
        self._create_base_path()

    def _create_base_path(self) -> None:
        if isinstance(self.storage_client, LocalStorageClient):
            Path(self.write_path).mkdir(parents=True, exist_ok=True)

    def on_start(self) -> None:
        self._fd = self.storage_client.open(self.filepath, self._mode)


def list_team_name_info(registry: CardRegistry, team: Optional[str] = None) -> ListTeamNameInfo:
    """Returns dictionary of teams and info"""

    all_teams = registry._registry.unique_teams  # pylint: disable=protected-access

    if not bool(all_teams):
        default_team = None
    else:
        default_team = all_teams[0]

    team = team or default_team
    names = registry._registry.get_unique_card_names(team=team)  # pylint: disable=protected-access

    return ListTeamNameInfo(
        teams=all_teams,
        selected_team=team,
        names=names,
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
                audit_card = cast(AuditCard, self.registries.audit.load_card(uid=self.audit_form_dict["uid"]))

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


def write_records_to_csv(
    records: List[Dict[str, Optional[Union[str, int]]]],
    field_names: List[str],
) -> StreamingResponse:
    """Writes audit data to csv and returns FileResponse

    Args:
        records:
            List of audit records
        field_names:
            List of field names for csv header

    Returns:
        FileResponse
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(records)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "filename=audit_file.csv"},
    )
