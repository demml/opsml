# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional, Tuple, cast

import pandas as pd
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import api_routes, ApiClient

from opsml.registry.sql.base.registry_base import SQLRegistryBase, settings
from opsml.registry.sql.base.query_engine import log_card_change  # type: ignore
from opsml.registry.sql.semver import CardVersion, VersionType

logger = ArtifactLogger.get_logger()


class ClientRegistry(SQLRegistryBase):
    def __init__(self, table_name: str):
        super().__init__(table_name)

        self._session = self._get_session()

    def _get_session(self) -> ApiClient:
        """Gets the requests session for connecting to the opsml api"""
        return cast(ApiClient, settings.request_client)

    def check_uid(self, uid: str, table_to_check: str) -> bool:
        data = self._session.post_request(
            route=api_routes.CHECK_UID,
            json={"uid": uid, "table_name": table_to_check},
        )

        return bool(data.get("uid_exists"))

    def set_version(
        self,
        name: str,
        team: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType = VersionType.MINOR,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        if supplied_version is not None:
            version_to_send = supplied_version.model_dump()
        else:
            version_to_send = None

        data = self._session.post_request(
            route=api_routes.VERSION,
            json={
                "name": name,
                "team": team,
                "version": version_to_send,
                "version_type": version_type,
                "table_name": self.table_name,
                "pre_tag": pre_tag,
                "build_tag": build_tag,
            },
        )

        return str(data["version"])

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves records from registry

        Args:
            name:
                Card Name
            team:
                Team Card
            version:
                Version. If not specified, the most recent version will be used.
            uid:
                Unique identifier for an ArtifactCard. If present, the uid takes precedence.
            tags:
                Tags associated with a given ArtifactCard
            max_date:
                Max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01")
            limit:
                Places a limit on result list. Results are sorted by SemVer
            ignore_release_candidates:
                If True, release candidates will be ignored

        Returns:
            Dictionary of card records
        """
        data = self._session.post_request(
            route=api_routes.LIST_CARDS,
            json={
                "name": name,
                "team": team,
                "version": version,
                "uid": uid,
                "max_date": max_date,
                "limit": limit,
                "tags": tags,
                "table_name": self.table_name,
                "ignore_release_candidates": ignore_release_candidates,
            },
        )

        return data["cards"]

    @log_card_change
    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.post_request(
            route=api_routes.CREATE_CARD,
            json={
                "card": card,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("registered")):
            return card, "registered"
        raise ValueError("Failed to register card")

    @log_card_change
    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.post_request(
            route=api_routes.UPDATE_CARD,
            json={
                "card": card,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("updated")):
            return card, "updated"
        raise ValueError("Failed to update card")

    @log_card_change
    def delete_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.post_request(
            route=api_routes.DELETE_CARD,
            json={
                "card": card,
                "table_name": self.table_name,
            },
        )

        if bool(data.get("deleted")):
            return card, "deleted"
        raise ValueError("Failed to delete card")

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError
