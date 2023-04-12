from typing import Any, Dict, Iterable, List, Optional, Union, cast

import pandas as pd
from sqlalchemy.sql.expression import ColumnElement, FromClause

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import (
    ArtifactCard,
    DataCard,
    ModelCard,
    PipelineCard,
    RunCard,
)
from opsml_artifacts.registry.sql.records import (
    DataRegistryRecord,
    ModelRegistryRecord,
    PipelineRegistryRecord,
    RunRegistryRecord,
)
from opsml_artifacts.registry.sql.registry_base import (
    OpsmlRegistry,
    SQLRegistryBase,
    VersionType,
)
from opsml_artifacts.registry.sql.sql_schema import RegistryTableNames

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]

# ignoring class inheritance mypy error because OpsmlRegistry is a dynamic Class (Server or Client)


class DataCardRegistry(OpsmlRegistry):  # type:ignore
    def update_card(self, card: DataCard) -> None:
        """
        Updates an existing data card in the data registry.

        Args:
            data_card:
                Existing data card record
        """

        record = DataRegistryRecord(**card.dict())
        self.update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.DATA


class ModelCardRegistry(OpsmlRegistry):  # type:ignore
    def update_card(self, card: ModelCard) -> None:
        """Updates an existing model card.

        Args:
            model_card: Existing model card record
        """

        record = ModelRegistryRecord(**card.dict())
        self.update_record(record=record.dict())

    def _get_data_table_name(self) -> str:
        return RegistryTableNames.DATA.value

    def _validate_datacard_uid(self, uid: str) -> None:
        table_to_check = self._get_data_table_name()
        exists = self.check_uid(uid=uid, table_to_check=table_to_check)
        if not exists:
            raise ValueError("ModelCard must be assoicated with a valid DataCard uid")

    def _has_datacard_uid(self, uid: Optional[str]) -> bool:
        return bool(uid)

    def register_card(
        self,
        card: ModelCard,
        version_type: VersionType = VersionType.MINOR,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                Card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor"
            save_path:
                Blob path to save card artifacts to. SHOULD NOT include the base
                prefix (e.g. "gs://my_bucket") - this prefix is already inferred
                using either "OPSML_TRACKING_URI" or "OPSML_STORAGE_URI" env
                variables. In addition, save_path should specify a directory.
        """

        model_card = cast(ModelCard, card)

        if not self._has_datacard_uid(uid=model_card.datacard_uid):
            raise ValueError("""ModelCard must be associated with a valid DataCard uid""")

        if model_card.datacard_uid is not None:
            self._validate_datacard_uid(uid=model_card.datacard_uid)

        return super().register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.MODEL


class RunCardRegistry(OpsmlRegistry):  # type:ignore
    def update_card(self, card: RunCard) -> None:
        """
        Updates an existing experiment card in the registry.

        Args:
            card:
                Existing experiment card
        """

        record = RunRegistryRecord(**card.dict())
        self.update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.RUN


class PipelineCardRegistry(OpsmlRegistry):  # type:ignore
    def update_card(self, card: PipelineCard) -> None:
        """
        Updates an existing pipeline card in the pipeline registry.

        Args:
            card:
                Existing pipeline card
        """

        record = PipelineRegistryRecord(**card.dict())
        self.update_record(record=record.dict())

    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PIPELINE


class ProjectCardRegistry(OpsmlRegistry):  # type:ignore
    @staticmethod
    def validate(registry_name: str):
        return registry_name in RegistryTableNames.PROJECT


# CardRegistry also needs to set a storage file system
class CardRegistry:
    def __init__(self, registry_name: str):
        """Interface for connecting to any of the ArtifactCard registries

        Args:
            registry_name:
                Name of the registry to connect to. Options are "pipeline",
                "model", "data" and "experiment".

        Returns:
            Instantiated connection to specific Card registry

        Example:
            # With connection type cloud_sql = CloudSQLConnection(...)
            data_registry = CardRegistry(registry_name="data",
            connection_client=cloud_sql)

            # With connection client data_registry =
            CardRegistry(registry_name="data", connection_type="gcp")
        """

        self.registry: SQLRegistryBase = self._set_registry(registry_name=registry_name)
        self.table_name = self.registry._table.__tablename__

    def _set_registry(self, registry_name: str) -> OpsmlRegistry:  # type:ignore
        """Returns a SQL registry to be used to register Cards

        Args:
            registry_name: Name of the registry (pipeline, model, data, experiment)

        Returns:
            SQL Registry
        """

        registry_name = RegistryTableNames[registry_name.upper()].value
        registry = next(
            registry
            for registry in OpsmlRegistry.__subclasses__()
            if registry.validate(
                registry_name=registry_name,
            )
        )

        return registry(table_name=registry_name)

    def list_cards(
        self,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
    ) -> pd.DataFrame:
        """Retrieves records from registry

        Args:
            name:
                Card name
            team:
                Team associated with card
            version:
                Optional version number of existing data. If not specified, the
                most recent version will be used
            uid:
                Unique identifier for Card. If present, the uid takes precedence.

        Returns:
            pandas dataframe of records
        """

        if name is not None:
            name = name.lower()

        if team is not None:
            team = team.lower()

        card_list = self.registry.list_cards(uid=uid, name=name, team=team, version=version)
        return pd.DataFrame(card_list)

    def load_card(
        self,
        name: Optional[str] = None,
        team: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ArtifactCard:
        """Loads a specific card

        Args:
            name:
                Optional Card name
            team:
                Optional team associated with card
            uid:
                Unique identifier for card. If present, the uid takes
                precedence.
            version:
                Optional version number of existing data. If not specified, the
                most recent version will be used

        Returns
            ArtifactCard
        """
        if name is not None:
            name = name.lower()
            name = name.replace("_", "-")

        if team is not None:
            team = team.lower()

        return self.registry.load_card(uid=uid, name=name, team=team, version=version)

    def register_card(
        self,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Adds new record to registry.

        Args:
            card:
                card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor".
            save_path:
                Blob path to save card artifacts too. This path SHOULD NOT
                include the base prefix (e.g. "gs://my_bucket") - this prefix is
                already inferred using either "OPSML_TRACKING_URI" or
                "OPSML_STORAGE_URI" env variables. In addition, save_path should
                specify a directory.
        """

        self.registry.register_card(
            card=card,
            version_type=version_type,
            save_path=save_path,
        )

    def update_card(
        self,
        card: ArtifactCard,
    ) -> None:
        """
        Update and artifact card (DataCard only) based on current registry

        Args:
            card:
                Card to register
        """

        if not hasattr(self.registry, "update_card"):
            raise ValueError(f"""{card.__class__.__name__} has no 'update_card' attribute""")

        self.registry = cast(DataCardRegistry, self.registry)
        card = cast(DataCard, card)
        return self.registry.update_card(card=card)

    def query_value_from_card(self, uid: str, columns: List[str]) -> Dict[str, Any]:
        """
        Query column values from a specific Card

        Args:
            uid:
                Uid of Card
            columns:
                List of columns to query

        Returns:
            Dictionary of column, values pairs
        """
        results = self.registry.list_cards(uid=uid)[0]  # pylint: disable=protected-access
        return {col: results[col] for col in columns}
