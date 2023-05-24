from functools import wraps
from typing import Any, Iterable, Optional, Type, Union, cast

from sqlalchemy import select
from sqlalchemy.sql import FromClause, Select
from sqlalchemy.sql.expression import ColumnElement

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.semver import get_version_to_search
from opsml.registry.sql.sql_schema import REGISTRY_TABLES, TableSchema

logger = ArtifactLogger.get_logger(__name__)


SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]


class QueryCreator:
    def create_version_query(
        self,
        table: Type[REGISTRY_TABLES],
        name: str,
        team: str,
    ) -> Select:
        """Creates query to get latest card version"""
        return (
            select(table)
            .filter(
                table.name == name,
                table.team == team,
            )
            .order_by(table.timestamp.desc(), table.version.desc())
            .limit(20)  # type: ignore
        )

    def record_from_table_query(
        self,
        table: Type[REGISTRY_TABLES],
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Select:
        """Creates a sql query based on table, uid, name, team and version

        Args:
            table (Schema): Registry table to query
            uid (str): Optional unique id of Card
            name (str): Optional name of Card
            team (str): Optional team name
            version (str): Optional version of Card

        Returns
            Sqlalchemy Select statement
        """

        query = self._get_base_select_query(table=table)
        if bool(uid):
            return query.filter(table.uid == uid)

        filters = []
        for field, value in zip(["name", "team", "version"], [name, team, version]):
            if value is not None:
                if field == "version":
                    version = get_version_to_search(version=version)
                    filters.append(getattr(table, field).like(f"{version}%"))

                else:
                    filters.append(getattr(table, field) == value)

        if bool(filters):
            query = query.filter(*filters)

        query = query.order_by(table.version.desc(), table.timestamp.desc())  # type: ignore

        return query

    def _get_base_select_query(self, table: Type[REGISTRY_TABLES]) -> Select:
        sql_table = cast(SqlTableType, table)
        return cast(Select, select(sql_table))

    def uid_exists_query(self, uid: str, table_to_check: str) -> Select:
        table = TableSchema.get_table(table_name=table_to_check)
        query = self._get_base_select_query(table=table.uid)  # type: ignore
        query = query.filter(table.uid == uid)

        return cast(Select, query)


def log_card_change(func):
    """Decorator for logging card changes"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> None:
        card, state = func(self, *args, **kwargs)
        name = str(card.get("name"))
        version = str(card.get("version"))
        logger.info(
            "%s: %s, version:%s %s", self._table.__tablename__, name, version, state  # pylint: disable=protected-access
        )

    return wrapper
