# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import datetime
from functools import wraps
from typing import Any, Dict, Iterable, Optional, Type, Union, cast, List, Iterator
from contextlib import contextmanager
from sqlalchemy import select
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import FromClause, Select
from sqlalchemy.sql.expression import ColumnElement
from opsml.registry.utils.settings import settings
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.semver import get_version_to_search
from opsml.registry.sql.sql_schema import REGISTRY_TABLES, TableSchema

logger = ArtifactLogger.get_logger()

SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
YEAR_MONTH_DATE = "%Y-%m-%d"


class QueryEngine:
    def __init__(self):
        self.engine = settings.sql_engine

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

        query = self._get_base_select_query(table=table)
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

        query = query.order_by(table.version.desc(), table.timestamp.desc())  # type: ignore

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
    ) -> List[Dict[str, Any]]:
        query = self._records_from_table_query(
            table=table, uid=uid, name=name, team=team, version=version, max_date=max_date, tags=tags
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
