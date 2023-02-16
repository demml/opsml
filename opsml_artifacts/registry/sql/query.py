from typing import Any, Iterable, List, Optional, Type, Union, cast

from sqlalchemy import select
from sqlalchemy.sql import FromClause, Select
from sqlalchemy.sql.expression import ColumnElement

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.cards.cards import (
    DataCard,
    ExperimentCard,
    ModelCard,
    PipelineCard,
)
from opsml_artifacts.registry.sql.sql_schema import REGISTRY_TABLES, TableSchema

logger = ArtifactLogger.get_logger(__name__)

ArtifactCardTypes = Union[ModelCard, DataCard, ExperimentCard, PipelineCard]

SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]


class QueryCreatorMixin:
    def _list_records_from_table(
        self,
        table: Type[REGISTRY_TABLES],
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
    ) -> Select:

        query = self._get_base_select_query(table=table)
        if bool(uid):
            return self._filter_query(query=query, field="uid", value=uid, table=table)

        query = self._multi_filter_query(
            query=query,
            fields=["name", "team", "version"],
            values=[name, team, version],
            table=table,
        )
        return query

    def _query_record_from_table(
        self,
        table: Type[REGISTRY_TABLES],
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[int] = None,
        uid: Optional[str] = None,
    ) -> Select:

        query = self._get_base_select_query(table=table)
        if bool(uid):
            return self._filter_query(query=query, field="uid", value=uid, table=table)

        if not any([name, team]):
            raise ValueError(
                """If no uid is supplied then name and team are required.
            Version can also be supplied with version and team."""
            )

        query = self._multi_filter_query(
            query=query,
            fields=["name", "team", "version"],
            values=[name, team, version],
            table=table,
        )
        return query

    def _get_base_select_query(self, table: Type[REGISTRY_TABLES]) -> Select:
        sql_table = cast(SqlTableType, table)
        return cast(Select, select(sql_table))

    def _multi_filter_query(
        self,
        query: Select,
        fields: List[str],
        values: List[Union[Optional[str], Optional[int]]],
        table: Type[REGISTRY_TABLES],
    ) -> Select:
        for field, value in zip(fields, values):
            query = self._filter_query(query=query, field=field, value=value, table=table)
        return query

    def _filter_query(
        self, query: Select, field: str, value: Union[Optional[str], Optional[int]], table: Type[REGISTRY_TABLES]
    ) -> Select:
        if value is None and field != "version":
            return query
        if value is None and field == "version":
            return query.order_by(table.version.desc())  # type: ignore
        return query.where(getattr(table, field) == value)

    def _query_if_uid_exists(self, uid: str, table_to_check: str) -> Select:

        table = TableSchema.get_table(table_name=table_to_check)
        select_query = self._get_base_select_query(table=table.uid)  # type: ignore
        query = self._filter_query(query=select_query, field="uid", value=uid, table=table)

        return cast(Select, query)
