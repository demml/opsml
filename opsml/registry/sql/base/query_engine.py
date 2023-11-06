# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import datetime
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Iterable, Iterator, List, Optional, Type, Union, cast

from sqlalchemy import Integer
from sqlalchemy import func as sqa_func
from sqlalchemy import select, text
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import FromClause, Select
from sqlalchemy.sql.expression import ColumnElement

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.semver import get_version_to_search
from opsml.registry.sql.sql_schema import REGISTRY_TABLES, TableSchema
from opsml.registry.utils.settings import settings

logger = ArtifactLogger.get_logger()

SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
YEAR_MONTH_DATE = "%Y-%m-%d"


class VersionSplitting:
    """
    Class containing logic for splitting version into major, minor, patch
    depending on sql dialect
    """

    @staticmethod
    def sqlite(query: Select, table: Type[REGISTRY_TABLES]) -> Select:
        return query.add_columns(  # type: ignore[attr-defined]
            sqa_func.cast(sqa_func.substr(table.version, 0, sqa_func.instr(table.version, ".")), Integer).label(
                "major"
            ),
            sqa_func.cast(
                sqa_func.substr(
                    sqa_func.substr(table.version, sqa_func.instr(table.version, ".") + 1),
                    1,
                    sqa_func.instr(sqa_func.substr(table.version, sqa_func.instr(table.version, ".") + 1), ".") - 1,
                ),
                Integer,
            ).label("minor"),
            sqa_func.substr(
                sqa_func.substr(table.version, sqa_func.instr(table.version, ".") + 1),
                sqa_func.instr(sqa_func.substr(table.version, sqa_func.instr(table.version, ".") + 1), ".") + 1,
            ).label("patch"),
        )

    @staticmethod
    def postgres(query: Select, table: Type[REGISTRY_TABLES]) -> Select:
        return query.add_columns(  # type: ignore[attr-defined]
            sqa_func.cast(sqa_func.split_part(table.version, ".", 1), Integer).label("major"),
            sqa_func.cast(sqa_func.split_part(table.version, ".", 2), Integer).label("minor"),
            sqa_func.cast(
                sqa_func.regexp_replace(sqa_func.split_part(table.version, ".", 3), "[^0-9]+", "", "g"),
                Integer,
            ).label("patch"),
        )

    @staticmethod
    def mysql(query: Select, table: Type[REGISTRY_TABLES]) -> Select:
        return query.add_columns(  # type: ignore[attr-defined]
            sqa_func.cast(sqa_func.substring_index(table.version, ".", 1), Integer).label("major"),
            sqa_func.cast(
                sqa_func.substring_index(sqa_func.substring_index(table.version, ".", 2), ".", -1), Integer
            ).label("minor"),
            sqa_func.cast(
                sqa_func.regexp_replace(sqa_func.substring_index(table.version, ".", -1), "[^0-9]+", ""), Integer
            ).label("patch"),
        )

    @staticmethod
    def get_version_split_query(query: Select, table: Type[REGISTRY_TABLES], dialect: str) -> Select:
        if "sqlite" in dialect:
            return VersionSplitting.sqlite(query=query, table=table)
        if "postgres" in dialect:
            return VersionSplitting.postgres(query=query, table=table)
        if "mysql" in dialect:
            return VersionSplitting.mysql(query=query, table=table)
        raise ValueError(f"Unsupported dialect: {dialect}")


class QueryEngine:
    def __init__(self):
        self.engine = settings.sql_engine

    @property
    def dialect(self) -> str:
        return str(self.engine.url)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self.engine) as sess:  # type: ignore
            yield sess

    def _create_version_query(
        self,
        table: Type[REGISTRY_TABLES],
        name: str,
        version: Optional[str] = None,
    ) -> Select:
        """Creates query to get latest card version

        Args:
            table:
                Registry table to query
            name:
                Name of the card
            version:
                Version of the card
        Returns:
            Query to get latest card version
        """
        table_select = select(table).filter(table.name == name)  # type: ignore

        if version is not None:
            table_select = table_select.filter(table.version.like(f"{version}%"))  # type: ignore

        return table_select.order_by(table.timestamp.desc(), table.version.desc()).limit(20)  # type: ignore

    def get_versions(
        self,
        table: Type[REGISTRY_TABLES],
        name: str,
        version: Optional[str] = None,
    ) -> List[Any]:
        """Return all versions of a card

        Args:
            table:
                Registry table to query
            name:
                Name of the card
            version:
                Version of the card

        Returns:
            List of all versions of a card
        """
        query = self._create_version_query(table=table, name=name, version=version)

        with self.session() as sess:
            results = sess.scalars(query).all()  # type: ignore[attr-defined]

        return results

    def _records_from_table_query(
        self,
        table: Type[REGISTRY_TABLES],
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> Select:
        """
        Creates a sql query based on table, uid, name, team and version

        Args:
            table:
                Registry table to query
            uid:
                Optional unique id of Card
            name:
                Optional name of Card
            team:
                Optional team name
            version:
                Optional version of Card
            tags:
                Optional card tags
            max_date:
                Optional max date to search

        Returns
            Sqlalchemy Select statement
        """
        query: Select = self._get_base_select_query(table=table)
        query = VersionSplitting.get_version_split_query(
            query=query,
            table=table,
            dialect=self.dialect,
        )

        if bool(uid):
            return query.filter(table.uid == uid)  # type: ignore

        filters = []

        for field, value in zip(["name", "team"], [name, team]):
            if value is not None:
                filters.append(getattr(table, field) == value)

        if version is not None:
            version = get_version_to_search(version=version)
            filters.append(getattr(table, "version").like(f"{version}%"))

        if max_date is not None:
            max_date_ts = self._get_epoch_time_to_search(max_date=max_date)
            filters.append(getattr(table, "timestamp") <= max_date_ts)

        if tags is not None:
            for key, value in tags.items():
                filters.append(table.tags[key].as_string() == value)  # type: ignore

        if bool(filters):
            query = query.filter(*filters)  # type: ignore

        query = query.order_by(text("major desc"), text("minor desc"), text("patch desc"))  # type: ignore

        if limit is not None:
            query = query.limit(limit)

        return query

    def _parse_records(self, records: List[Any]) -> List[Dict[str, Any]]:
        """
        Helper for parsing sql results

        Args:
            results:
                Returned object sql query

        Returns:
            List of dictionaries
        """
        record_list: List[Dict[str, Any]] = []

        for row in records:
            result_dict = row[0].__dict__
            result_dict.pop("_sa_instance_state")
            record_list.append(result_dict)

        return record_list

    def get_records_from_table(
        self,
        table: Type[REGISTRY_TABLES],
        uid: Optional[str] = None,
        name: Optional[str] = None,
        team: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = self._records_from_table_query(
            table=table,
            uid=uid,
            name=name,
            team=team,
            version=version,
            max_date=max_date,
            tags=tags,
            limit=limit,
        )

        with self.session() as sess:
            results = sess.execute(query).all()

        return self._parse_records(results)

    def _get_epoch_time_to_search(self, max_date: str):
        """
        Creates timestamp that represents the max epoch time to limit records to

        Args:
            max_date:
                max date to search

        Returns:
            time stamp as integer related to `max_date`
        """
        converted_date = datetime.datetime.strptime(max_date, YEAR_MONTH_DATE)
        max_date_: datetime.datetime = converted_date.replace(
            hour=23, minute=59, second=59
        )  # provide max values for a date

        # opsml timestamp records are stored as BigInts
        return int(round(max_date_.timestamp() * 1_000_000))

    def _get_base_select_query(self, table: Type[REGISTRY_TABLES]) -> Select:
        sql_table = cast(SqlTableType, table)
        return cast(Select, select(sql_table))

    def _uid_exists_query(self, uid: str, table_to_check: str) -> Select:
        table = TableSchema.get_table(table_name=table_to_check)
        query = self._get_base_select_query(table=table.uid)  # type: ignore
        query = query.filter(table.uid == uid)  # type: ignore

        return cast(Select, query)

    def get_uid(self, uid: str, table_to_check: str) -> List[Any]:
        query = self._uid_exists_query(uid=uid, table_to_check=table_to_check)

        with self.session() as sess:
            results = sess.execute(query).first()

        return results

    def add_and_commit_card(
        self,
        table: Type[REGISTRY_TABLES],
        card: Dict[str, Any],
    ) -> None:
        """Add card record to table

        Args:
            table:
                table to add card to
            card:
                card to add
        """
        sql_record = table(**card)

        with self.session() as sess:
            sess.add(sql_record)
            sess.commit()

    def update_card_record(
        self,
        table: Type[REGISTRY_TABLES],
        card: Dict[str, Any],
    ):
        record_uid = cast(str, card.get("uid"))
        with self.session() as sess:
            query = sess.query(table).filter(table.uid == record_uid)
            query.update(card)
            sess.commit()

    def delete_card_record(
        self,
        table: Type[REGISTRY_TABLES],
        card: Dict[str, Any],
    ):
        record_uid = cast(str, card.get("uid"))
        with self.session() as sess:
            query = sess.query(table).filter(table.uid == record_uid)
            query.delete()
            sess.commit()


def log_card_change(func):
    """Decorator for logging card changes"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> None:
        card, state = func(self, *args, **kwargs)
        name = str(card.get("name"))
        version = str(card.get("version"))
        logger.info(
            "{}: {}, version:{} {}", self._table.__tablename__, name, version, state  # pylint: disable=protected-access
        )

    return wrapper
