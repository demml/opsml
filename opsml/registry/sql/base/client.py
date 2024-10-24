# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=abstract-method

import textwrap
from functools import cached_property
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

import pandas as pd

from opsml.cards import Card, ModelCard
from opsml.cards.project import ProjectCard
from opsml.helpers.exceptions import CardDeleteError
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import check_package_exists
from opsml.registry.semver import CardVersion, VersionType
from opsml.registry.sql.base.registry_base import SQLRegistryBase
from opsml.registry.sql.base.utils import log_card_change
from opsml.scouter.integration import ScouterClient
from opsml.storage.api import RequestType, api_routes
from opsml.storage.client import ApiStorageClient, StorageClient
from opsml.types import RegistryType

logger = ArtifactLogger.get_logger()


class ClientRegistry(SQLRegistryBase):
    """A registry that retrieves data from an opsml server instance."""

    def __init__(self, registry_type: RegistryType, storage_client: StorageClient):
        super().__init__(registry_type, storage_client)

        assert isinstance(storage_client, ApiStorageClient)

        self._session = storage_client.api_client
        self._registry_type = registry_type
        self._scouter_client = ScouterClient()

    @cached_property
    def table_name(self) -> str:
        """Returns the table name for this registry type"""
        data = self._session.request(
            route=api_routes.TABLE_NAME,
            request_type=RequestType.GET,
            params={"registry_type": self.registry_type.value},
        )

        return cast(str, data["table_name"])

    @property
    def registry_type(self) -> RegistryType:
        """Registry type"""
        raise NotImplementedError

    @staticmethod
    def validate(registry_name: str) -> bool:
        raise NotImplementedError

    @property
    def unique_repositories(self) -> Sequence[str]:
        """Returns a list of unique repositories"""
        data = self._session.request(
            route=api_routes.REPOSITORY_CARDS,
            request_type=RequestType.GET,
            params={"registry_type": self.registry_type.value},
        )

        return cast(List[str], data["repositories"])

    def check_uid(self, uid: str, registry_type: RegistryType) -> bool:
        data = self._session.request(
            route=api_routes.CHECK_UID,
            request_type=RequestType.POST,
            json={"uid": uid, "registry_type": registry_type.value},
        )

        return bool(data.get("uid_exists"))

    def set_version(
        self,
        name: str,
        repository: str,
        pre_tag: str,
        build_tag: str,
        version_type: VersionType = VersionType.MINOR,
        supplied_version: Optional[CardVersion] = None,
    ) -> str:
        if supplied_version is not None:
            version_to_send = supplied_version.model_dump()
        else:
            version_to_send = None

        data = self._session.request(
            route=api_routes.VERSION,
            request_type=RequestType.POST,
            json={
                "name": name,
                "repository": repository,
                "version": version_to_send,
                "version_type": version_type,
                "registry_type": self._registry_type.value,
                "pre_tag": pre_tag,
                "build_tag": build_tag,
            },
        )

        return str(data["version"])

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_date: Optional[str] = None,
        limit: Optional[int] = None,
        ignore_release_candidates: bool = False,
        query_terms: Optional[Dict[str, Any]] = None,
        sort_by_timestamp: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves records from registry

        Args:
            name:
                Card Name
            repository:
                Card Repository
            version:
                Version. If not specified, the most recent version will be used.
            uid:
                Unique identifier for an Card. If present, the uid takes precedence.
            tags:
                Tags associated with a given Card
            max_date:
                Max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01")
            limit:
                Places a limit on result list. Results are sorted by SemVer
            ignore_release_candidates:
                If True, release candidates will be ignored
            query_terms:
                Dictionary of query terms to filter by
            sort_by_timestamp:
                If True, sorts by timestamp descending

        Returns:
            Dictionary of card records
        """
        data = self._session.request(
            route=api_routes.LIST_CARDS,
            request_type=RequestType.POST,
            json={
                "name": name,
                "repository": repository,
                "version": version,
                "uid": uid,
                "max_date": max_date,
                "limit": limit,
                "tags": tags,
                "registry_type": self.registry_type.value,
                "ignore_release_candidates": ignore_release_candidates,
                "query_terms": query_terms,
                "sort_by_timestamp": sort_by_timestamp,
            },
        )

        return data["cards"]

    @log_card_change
    def add_and_commit(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.request(
            route=api_routes.CREATE_CARD,
            request_type=RequestType.POST,
            json={
                "card": card,
                "registry_type": self.registry_type.value,
            },
        )

        if bool(data.get("registered")):
            return card, "registered"
        raise ValueError("Failed to register card")

    @log_card_change
    def update_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.request(
            route=api_routes.UPDATE_CARD,
            request_type=RequestType.POST,
            json={
                "card": card,
                "registry_type": self.registry_type.value,
            },
        )

        if bool(data.get("updated")):
            return card, "updated"
        raise ValueError("Failed to update card")

    @log_card_change
    def delete_card_record(self, card: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        data = self._session.request(
            route=api_routes.DELETE_CARD,
            request_type=RequestType.POST,
            json={
                "card": card,
                "registry_type": self.registry_type.value,
            },
        )

        if bool(data.get("deleted")):
            return card, "deleted"
        raise CardDeleteError("Failed to delete card")


class ClientDataCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.DATA

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.DATA.value


class ClientModelCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.MODEL

    def _validate_datacard_uid(self, uid: str) -> None:
        exists = self.check_uid(uid=uid, registry_type=RegistryType.DATA)
        if not exists:
            raise ValueError("ModelCard must be associated with a valid DataCard uid")

    def register_card(
        self,
        card: Card,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                Card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor"
            pre_tag:
                pre-release tag
            build_tag:
                build tag
        """

        if card.uid is not None:
            logger.info(
                textwrap.dedent(
                    f"""
                Card {card.uid} already exists. Skipping registration. If you'd like to register
                a new card, please instantiate a new Card object. If you'd like to update the
                existing card, please use the update_card method.
                """
                )
            )

        else:
            card = cast(ModelCard, card)

            if card.to_onnx:
                if not check_package_exists("onnx"):
                    raise ModuleNotFoundError(
                        """To convert a model to onnx, please install onnx via one of the extras
                        (opsml[sklearn_onnx], opsml[tf_onnx], opsml[torch_onnx]) or set to_onnx to False.
                        """
                    )

            if card.datacard_uid is not None:
                self._validate_datacard_uid(uid=card.datacard_uid)

            super().register_card(
                card=card,
                version_type=version_type,
                pre_tag=pre_tag,
                build_tag=build_tag,
            )

            # write profile to scouter
            if card.interface.drift_profile and self._scouter_client.server_running:
                try:
                    self._scouter_client.insert_drift_profile(
                        drift_profile=card.interface.drift_profile.model_dump_json(),
                        drift_type=card.interface.drift_profile.config.drift_type,
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    logger.error(f"Failed to insert drift profile: {exc}")

    def update_card(self, card: Card) -> None:
        """
        Update an artifact card based on current registry

        Args:
            card:
                Card to register
        """
        card = cast(ModelCard, card)

        if card.datacard_uid is not None:
            self._validate_datacard_uid(uid=card.datacard_uid)

        super().update_card(card)

        # write profile to scouter
        if card.interface.drift_profile and self._scouter_client.server_running:
            try:
                self._scouter_client.update_drift_profile(
                    repository=card.repository,
                    name=card.name,
                    version=card.version,
                    drift_profile=card.interface.drift_profile.model_dump_json(),
                    drift_type=card.interface.drift_profile.config.drift_type,
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.error(f"Failed to update drift profile: {exc}")

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.MODEL.value


class ClientRunCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.RUN

    def insert_metric(self, metric: List[Dict[str, Any]]) -> None:
        """Inserts metrics into the run registry

        Args:
            metric:
                List of metric(s) to insert
        """

        self._session.request(
            route=api_routes.METRICS,
            request_type=RequestType.PUT,
            json={"metric": metric},
        )

    def insert_hw_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Inserts metrics into the run registry

        Args:
            metrics:
                List of hw metric(s) to insert
        """

        self._session.request(
            route=api_routes.HW_METRICS,
            request_type=RequestType.PUT,
            json={"metrics": metrics},
        )

    def get_metric(
        self,
        run_uid: str,
        name: Optional[List[str]] = None,
        names_only: bool = False,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get run metrics. By default, all metrics are returned. If name is provided,
        only metrics with that name are returned. Metric type can be either "metric" or "graph".
        "metric" will return name, value, step records. "graph" will return graph (x, y) records.

        Args:
            run_uid:
                Run uid
            name:
                Name of the metric
            names_only:
                Return only the names of the metrics

        Returns:
            List of run metrics
        """
        body = {"run_uid": run_uid}

        if name is not None:
            body["name"] = name

        if names_only:
            body["names_only"] = names_only

        data = self._session.request(route=api_routes.METRICS, request_type=RequestType.POST, json=body)

        metric = data.get("metric")
        return cast(Optional[List[Dict[str, Any]]], metric)

    def insert_parameter(self, parameter: List[Dict[str, Any]]) -> None:
        """Inserts parameters into the run registry
        Args:
            parameter:
                List of parameter(s) to insert
        """

        self._session.request(
            route=api_routes.PARAMETERS,
            request_type=RequestType.PUT,
            json={"parameter": parameter},
        )

    def get_parameter(self, run_uid: str, name: Optional[List[str]] = None) -> List[Optional[Dict[str, Any]]]:
        """Get run parameters. By default, all parameters are returned. If name is provided,
        only parameters with that name are returned.
        Args:
            run_uid:
                Run uid
            name:
                Name of the parameter
        Returns:
            List of run parameter
        """
        body = {"run_uid": run_uid}

        if name is not None:
            body["name"] = name

        data = self._session.request(route=api_routes.PARAMETERS, request_type=RequestType.POST, json=body)

        param = data.get("parameter")
        return cast(List[Optional[Dict[str, Any]]], param)

    def get_hw_metric(self, run_uid: str) -> Optional[List[Dict[str, Any]]]:
        """Gets run hardware metrics

        Args:
            run_uid:
                Run uid

        Returns:
            List of run metrics
        """

        data = self._session.request(
            route=api_routes.HW_METRICS,
            request_type=RequestType.GET,
            params={"run_uid": run_uid},
        )

        metric = data.get("metrics")
        return cast(Optional[List[Dict[str, Any]]], metric)

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.RUN.value


class ClientPipelineCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.PIPELINE

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.PIPELINE.value

    def delete_card(self, card: Card) -> None:
        raise ValueError("PipelineCardRegistry does not support delete_card")


class ClientProjectCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.PROJECT

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.PROJECT.value

    def register_card(
        self,
        card: Card,
        version_type: VersionType = VersionType.MINOR,
        pre_tag: str = "rc",
        build_tag: str = "build",
    ) -> None:
        """Registers a ProjectCard to the registry"""
        card = cast(ProjectCard, card)

        # set project id on card even if its already registered
        card.project_id = self.get_project_id(project_name=card.name, repository=card.repository)

        # check if ProjectCard already exists
        record = self.list_cards(name=card.name, repository=card.repository, limit=1)
        if record:
            return None

        return super().register_card(card, version_type, pre_tag, build_tag)

    def get_project_id(self, project_name: str, repository: str) -> int:
        """get project id from project name and repository

        Args:
            project_name:
                project name
            repository:
                repository name

        Returns:
            project id
        """

        data = self._session.request(
            route=api_routes.PROJECT_ID,
            request_type=RequestType.GET,
            params={
                "project_name": project_name,
                "repository": repository,
            },
        )

        project_id = data.get("project_id")

        assert isinstance(project_id, int)
        return project_id

    def delete_card(self, card: Card) -> None:
        raise ValueError("ProjectCardRegistry does not support delete_card")


class ClientAuditCardRegistry(ClientRegistry):
    @property
    def registry_type(self) -> RegistryType:
        return RegistryType.AUDIT

    def validate_uid(self, uid: str, registry_type: RegistryType) -> bool:
        return self.check_uid(uid=uid, registry_type=registry_type)

    @staticmethod
    def validate(registry_name: str) -> bool:
        return registry_name.lower() == RegistryType.AUDIT.value
