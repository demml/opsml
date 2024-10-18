# mypy: disable-error-code="call-overload"
# pylint: disable=not-callable

# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import datetime
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union, cast

from sqlalchemy import Integer, and_
from sqlalchemy import cast as sql_cast
from sqlalchemy import func as sqa_func
from sqlalchemy import insert, select, text
from sqlalchemy.engine import Engine, Row
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import FromClause, Select, distinct, or_
from sqlalchemy.sql.expression import ColumnElement

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.semver import get_version_to_search
from opsml.registry.sql.base.sql_schema import (
    AuthSchema,
    CardSQLTable,
    HardwareMetricSchema,
    MessageSchema,
    MetricSchema,
    ParameterSchema,
    ProjectSchema,
    SQLTableGetter,
)
from opsml.types import RegistryType
from opsml.types.extra import Message, User

logger = ArtifactLogger.get_logger()

SqlTableType = Optional[Iterable[Union[ColumnElement[Any], FromClause, int]]]
YEAR_MONTH_DATE = "%Y-%m-%d"


class SqlDialect(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE_MEMORY = ":memory:"


class DialectHelper:
    def __init__(self, query: Select[Any], table: CardSQLTable):
        """Instantiates a dialect helper"""
        self.query = query
        self.table = table

    def get_version_split_logic(self) -> Select[Any]:
        """Defines dialect specific logic to split version into major, minor, patch"""
        raise NotImplementedError

    @staticmethod
    def validate_dialect(dialect: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def get_dialect_logic(query: Select[Any], table: CardSQLTable, dialect: str) -> Select[Any]:
        helper = next(
            (dialect_helper for dialect_helper in DialectHelper.__subclasses__() if dialect_helper.validate_dialect(dialect)),
            None,
        )

        if helper is None:
            raise ValueError(f"Unsupported dialect: {dialect}")

        helper_instance = helper(query=query, table=table)

        return helper_instance.get_version_split_logic()


class SqliteHelper(DialectHelper):
    def get_version_split_logic(self) -> Select[Any]:
        return self.query.add_columns(
            sql_cast(sqa_func.substr(self.table.version, 0, sqa_func.instr(self.table.version, ".")), Integer).label("major"),
            sql_cast(
                sqa_func.substr(
                    sqa_func.substr(self.table.version, sqa_func.instr(self.table.version, ".") + 1),
                    1,
                    sqa_func.instr(sqa_func.substr(self.table.version, sqa_func.instr(self.table.version, ".") + 1), ".") - 1,
                ),
                Integer,
            ).label("minor"),
            sqa_func.substr(
                sqa_func.substr(self.table.version, sqa_func.instr(self.table.version, ".") + 1),
                sqa_func.instr(sqa_func.substr(self.table.version, sqa_func.instr(self.table.version, ".") + 1), ".") + 1,
            ).label("patch"),
        )

    @staticmethod
    def validate_dialect(dialect: str) -> bool:
        return SqlDialect.SQLITE in dialect


class PostgresHelper(DialectHelper):
    def get_version_split_logic(self) -> Select[Any]:
        return self.query.add_columns(
            sql_cast(sqa_func.split_part(self.table.version, ".", 1), Integer).label("major"),
            sql_cast(sqa_func.split_part(self.table.version, ".", 2), Integer).label("minor"),
            sql_cast(
                sqa_func.regexp_replace(sqa_func.split_part(self.table.version, ".", 3), "[^0-9]+", "", "g"),
                Integer,
            ).label("patch"),
        )

    @staticmethod
    def validate_dialect(dialect: str) -> bool:
        return SqlDialect.POSTGRES in dialect


class MySQLHelper(DialectHelper):
    def get_version_split_logic(self) -> Select[Any]:
        return self.query.add_columns(
            sql_cast(sqa_func.substring_index(self.table.version, ".", 1), Integer).label("major"),
            sql_cast(sqa_func.substring_index(sqa_func.substring_index(self.table.version, ".", 2), ".", -1), Integer).label(
                "minor"
            ),
            sql_cast(
                sqa_func.regexp_replace(sqa_func.substring_index(self.table.version, ".", -1), "[^0-9]+", ""),
                Integer,
            ).label("patch"),
        )

    @staticmethod
    def validate_dialect(dialect: str) -> bool:
        return SqlDialect.MYSQL in dialect


class QueryEngine:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @property
    def dialect(self) -> str:
        return str(self.engine.url)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self.engine) as sess:
            yield sess

    def _create_version_query(
        self,
        table: CardSQLTable,
        name: str,
        repository: str,
        version: Optional[str] = None,
    ) -> Select[Any]:
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
        table_select = select(table).filter(table.name == name, table.repository == repository)  # type: ignore

        if version is not None:
            table_select = table_select.filter(table.version.like(f"{version}%"))  # type: ignore

        return table_select.order_by(table.timestamp.desc(), table.version.desc()).limit(20)  # type: ignore

    def get_versions(
        self,
        table: CardSQLTable,
        name: str,
        repository: str,
        version: Optional[str] = None,
    ) -> List[Any]:
        """Return all versions of a card

        Args:
            table:
                Registry table to query
            name:
                Name of the card
            repository:
                Repository name
            version:
                Version of the card

        Returns:
            List of all versions of a card
        """
        query = self._create_version_query(table=table, name=name, version=version, repository=repository)

        with self.session() as sess:
            results = sess.scalars(query).all()

        return cast(List[Any], results)

    def _records_from_table_query(
        self,
        table: CardSQLTable,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        query_terms: Optional[Dict[str, Any]] = None,
        sort_by_timestamp: bool = False,
    ) -> Select[Any]:
        """
        Creates a sql query based on table, uid, name, repository and version

        Args:
            table:
                Registry table to query
            uid:
                Optional unique id of Card
            name:
                Optional name of Card
            repository:
                Optional Repository name
            version:
                Optional version of Card
            tags:
                Optional card tags
            max_date:
                Optional max date to search
            limit:
                Optional limit of records to return
            query_terms:
                Optional query terms to search

        Returns
            Sqlalchemy Select statement
        """

        query = cast(Select[Any], select(table))
        query = DialectHelper.get_dialect_logic(query=query, table=table, dialect=self.dialect)

        if bool(uid):
            return query.filter(table.uid == uid)  # type: ignore

        filters = []

        for field, value in zip(["name", "repository"], [name, repository]):
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

        if query_terms is not None:
            for field, value in query_terms.items():
                filters.append(getattr(table, field) == value)

        if bool(filters):
            query = query.filter(*filters)

        if not sort_by_timestamp:
            query = query.order_by(text("major desc"), text("minor desc"), text("patch desc"))
        else:
            query = query.order_by(table.timestamp.desc())  # type: ignore

        if limit is not None:
            query = query.limit(limit)

        return query

    def _parse_records(self, records: Sequence[Row[Any]]) -> List[Dict[str, Any]]:
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
        table: CardSQLTable,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        query_terms: Optional[Dict[str, Any]] = None,
        sort_by_timestamp: bool = False,
    ) -> List[Dict[str, Any]]:
        query = self._records_from_table_query(
            table=table,
            uid=uid,
            name=name,
            repository=repository,
            version=version,
            max_date=max_date,
            tags=tags,
            limit=limit,
            query_terms=query_terms,
            sort_by_timestamp=sort_by_timestamp,
        )

        with self.session() as sess:
            results = sess.execute(query).all()

        return self._parse_records(results)

    def _get_epoch_time_to_search(self, max_date: str) -> int:
        """
        Creates timestamp that represents the max epoch time to limit records to

        Args:
            max_date:
                max date to search

        Returns:
            time stamp as integer related to `max_date`
        """
        converted_date = datetime.datetime.strptime(max_date, YEAR_MONTH_DATE)
        max_date_: datetime.datetime = converted_date.replace(hour=23, minute=59, second=59)  # provide max values for a date

        # opsml timestamp records are stored as BigInts
        return int(round(max_date_.timestamp() * 1_000_000))

    def _uid_exists_query(self, uid: str, table_to_check: str) -> Select[Any]:
        table = SQLTableGetter.get_table(table_name=table_to_check)
        query = select(table).filter(table.uid == uid)

        return cast(Select[Any], query)

    def get_uid(self, uid: str, table_to_check: str) -> List[str]:
        query = self._uid_exists_query(uid=uid, table_to_check=table_to_check)

        with self.session() as sess:
            return cast(List[str], sess.execute(query).first())

    def add_and_commit_card(
        self,
        table: CardSQLTable,
        card: Dict[str, Any],
    ) -> None:
        """Add card record to table

        Args:
            table:
                table to add card to
            card:
                card to add
        """

        sql_record = table(**card)  # type:ignore[operator]

        with self.session() as sess:
            sess.add(sql_record)
            sess.commit()

    def update_card_record(
        self,
        table: CardSQLTable,
        card: Dict[str, Any],
    ) -> None:
        record_uid = cast(str, card.get("uid"))

        with self.session() as sess:
            query = sess.query(table).filter(table.uid == record_uid)
            query.update(card)
            sess.commit()

    def get_unique_repositories(self, table: CardSQLTable) -> Sequence[str]:
        """Retrieves unique repositories in a registry

        Args:
            table:
                Registry table to query

        Returns:
            List of unique repositories
        """

        repository_col = table.repository
        query = (
            select(repository_col).distinct().order_by(repository_col.asc())  # type:ignore[call-overload, union-attr]
        )

        with self.session() as sess:
            return sess.scalars(query).all()

    def get_unique_card_names(self, repository: Optional[str], table: CardSQLTable) -> Sequence[str]:
        """Returns a list of unique card names"""
        query = select(table.name)  # type:ignore[call-overload]

        if repository is not None:
            query = (
                query.filter(table.repository == repository).distinct().order_by(table.name.asc())  # type:ignore[union-attr]
            )  #
        else:
            query = query.distinct()

        with self.session() as sess:
            return sess.scalars(query).all()

    def query_stats(
        self,
        table: CardSQLTable,
        search_term: Optional[str],
    ) -> Dict[str, int]:
        """Query stats for a card registry
        Args:
            table:
                Registry table to query
            search_term:
                Search term
        """

        query = select(
            sqa_func.count(distinct(table.name)).label("nbr_names"),  # type: ignore
            sqa_func.count(table.version).label("nbr_versions"),  # type: ignore
            sqa_func.count(distinct(table.repository)).label("nbr_repos"),  # type: ignore
        )

        if search_term:
            query = query.filter(
                or_(
                    table.name.like(f"%{search_term}%"),  # type: ignore
                    table.repository.like(f"%{search_term}%"),  # type: ignore
                ),
            )

        with self.session() as sess:
            results = sess.execute(query).first()

        if not results:
            return {
                "nbr_names": 0,
                "nbr_versions": 0,
                "nbr_repos": 0,
            }
        return {
            "nbr_names": results[0],
            "nbr_versions": results[1],
            "nbr_repos": results[2],
        }

    def query_page(
        self,
        sort_by: str,
        page: int,
        search_term: Optional[str],
        repository: Optional[str],
        table: CardSQLTable,
    ) -> Sequence[Row[Any]]:
        """Returns a page result from card registry
        Args:
            sort_by:
                Field to sort by
            page:
                Page number
            search_term:
                Search term
            repository:
                Repository name
            table:
                Registry table to query
        Returns:
            Tuple of card summary
        """

        ## build versions
        versions = select(
            table.repository,
            table.name,
            table.version,
            sqa_func.row_number()
            .over(
                partition_by=(table.repository, table.name),  # type: ignore
                order_by=table.timestamp.desc(),  # type: ignore
            )
            .label("row_number"),
        )

        #### get summary stats for repo/name
        stats = select(
            table.repository,
            table.name,
            sqa_func.count(distinct(table.version)).label("versions"),  # type:ignore
            sqa_func.max(table.timestamp).label("updated_at"),
            sqa_func.min(table.timestamp).label("created_at"),
        ).group_by(table.repository, table.name)

        if repository is not None:
            versions = versions.filter(table.repository == repository)
            stats = stats.filter(table.repository == repository)

        if search_term:
            versions = versions.filter(
                or_(
                    table.name.like(f"%{search_term}%"),  # type: ignore
                    table.repository.like(f"%{search_term}%"),  # type: ignore
                ),
            )

            stats = stats.filter(
                or_(
                    table.name.like(f"%{search_term}%"),  # type: ignore
                    table.repository.like(f"%{search_term}%"),  # type: ignore
                ),
            )

        versions = versions.subquery()
        stats = stats.subquery()

        filtered_versions = (
            select(
                versions.c.repository,
                versions.c.name,
                versions.c.version,
                versions.c.row_number,
            )
            .filter(versions.c.row_number == 1)
            .subquery()
        )

        joined = (
            select(
                stats.c.repository,
                stats.c.name,
                filtered_versions.c.version,
                stats.c.versions,
                stats.c.updated_at,
                stats.c.created_at,
                sqa_func.row_number().over(order_by=sort_by).label("row_number"),
            )
            .join(
                filtered_versions,
                and_(
                    stats.c.repository == filtered_versions.c.repository,
                    stats.c.name == filtered_versions.c.name,
                ),
            )
            .subquery()
        )

        lower_bound = page * 30
        upper_bound = lower_bound + 30

        combined_query = (
            select(joined)
            .filter(joined.c.row_number.between(lower_bound, upper_bound))
            .order_by(
                joined.c.updated_at.desc(),
            )
        )

        with self.session() as sess:
            records = sess.execute(combined_query).all()

        return records

    def delete_card_record(
        self,
        table: CardSQLTable,
        card: Dict[str, Any],
    ) -> None:
        record_uid = cast(str, card.get("uid"))
        with self.session() as sess:
            query = sess.query(table).filter(table.uid == record_uid)
            query.delete()
            sess.commit()


class ProjectQueryEngine(QueryEngine):
    def get_max_project_id(self) -> int:
        """Get max project id

        Returns:
            Max project id or 0
        """
        query = select(sqa_func.max(ProjectSchema.project_id))
        with self.session() as sess:
            result = sess.execute(query).first()
            if not result:
                return 0

            max_project = result[0]

            if max_project:
                return cast(int, max_project)
            return 0

    def get_project_id(self, project_name: str, repository: str) -> int:
        """Get project id from project name and repository

        Args:
            project_name:
                Name of the project
            repository:
                Repository name

        Returns:
            Project id or None
        """
        query = select(ProjectSchema.project_id).filter(
            ProjectSchema.name == project_name,
            ProjectSchema.repository == repository,
        )
        with self.session() as sess:
            project_id = sess.execute(query).first()

            if project_id:
                return cast(int, project_id[0])

        return self.get_max_project_id() + 1


class RunQueryEngine(QueryEngine):
    def insert_metric(self, metric: List[Dict[str, Any]]) -> None:
        """Insert run metrics

        Args:
            metric:
                List of run metric(s)
        """
        with self.session() as sess:
            sess.execute(insert(MetricSchema), metric)
            sess.commit()

    def insert_hw_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Insert run metrics

        Args:
            metrics:
                List of run metric(s)
        """
        with self.session() as sess:
            sess.execute(insert(HardwareMetricSchema), metrics)
            sess.commit()

    def get_hw_metric(self, run_uid: str) -> Optional[List[Dict[str, Any]]]:
        """Get hardware metrics associated with a run.

        Args:
            run_uid:
                Run uid

        Returns:
            List of hardware metrics
        """

        query = select(HardwareMetricSchema).filter(HardwareMetricSchema.run_uid == run_uid)

        with self.session() as sess:
            results = sess.execute(query).all()
        if not results:
            return None

        return self._parse_records(results)

    def get_metric(
        self,
        run_uid: str,
        name: Optional[List[str]] = None,
        names_only: bool = False,
    ) -> List[Dict[str, Any]]:
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

        column_to_query = distinct(MetricSchema.name) if names_only else MetricSchema

        query = select(column_to_query).filter(MetricSchema.run_uid == run_uid)

        if name is not None:
            filters = [MetricSchema.name == n for n in name]
            query = query.filter(or_(*filters))

        with self.session() as sess:
            results = sess.execute(query).all()
        if not results:
            return []

        if names_only:
            return [row[0] for row in results]

        return self._parse_records(results)

    def insert_parameter(self, parameter: List[Dict[str, Any]]) -> None:
        """Insert run parameter
        Args:
            parameter:
                List of run parameter(s)
        """
        with self.session() as sess:
            sess.execute(insert(ParameterSchema), parameter)
            sess.commit()

    def get_parameter(self, run_uid: str, name: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get run parameters. By default, all parameters are returned. If name is provided,
        only parameters with that name are returned.
        Args:
            run_uid:
                Run uid
            name:
                Name of the parameter
        Returns:
            List of run metrics
        """

        query = select(ParameterSchema).filter(ParameterSchema.run_uid == run_uid)
        if name is not None:
            filters = [ParameterSchema.name == n for n in name]
            query = query.filter(or_(*filters))

        with self.session() as sess:
            results = sess.execute(query).all()

        if not results:
            return []

        return self._parse_records(results)


class AuthQueryEngine(QueryEngine):
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by username

        Args:
            email:
                Email

        Returns:
            User record
        """

        query = select(AuthSchema).filter(AuthSchema.email == email)
        with self.session() as sess:
            result = sess.execute(query).first()

        if not result:
            return None

        return User(**result[0].__dict__)

    def get_user(self, username: str) -> Optional[User]:
        """Get user by username

        Args:
            username:
                Username

        Returns:
            User record
        """

        query = select(AuthSchema).filter(AuthSchema.username == username)
        with self.session() as sess:
            result = sess.execute(query).first()

        if not result:
            return None

        return User(**result[0].__dict__)

    def add_user(self, user: User) -> None:
        """Add user

        Args:
            user:
                User record
        """
        dumped_model = user.model_dump(exclude={"password", "updated_username"})
        with self.session() as sess:
            sess.execute(insert(AuthSchema), dumped_model)
            sess.commit()

    def update_user(self, user: User) -> bool:
        """Update user

        Args:
            user:
                User record
        """

        updated = False
        current_username = user.username

        # handle updated username
        if user.updated_username:
            user.username = user.updated_username

        dumped_model = user.model_dump(exclude={"password", "updated_username"})

        with self.session() as sess:
            query = sess.query(AuthSchema).filter(AuthSchema.username == current_username)
            query.update(dumped_model)  # type: ignore
            sess.commit()
            updated = True

        return updated

    def delete_user(self, user: User) -> bool:
        """Delete user

        Args:
            user:
                User record
        """
        deleted = False
        with self.session() as sess:
            query = sess.query(AuthSchema).filter(AuthSchema.username == user.username)
            query.delete()
            sess.commit()
            deleted = True

        return deleted


class MessageQueryEngine(QueryEngine):
    def insert_message(self, message: Message) -> None:
        """Insert message

        Args:
            message:
                message record
        """

        with self.session() as sess:
            sess.execute(insert(MessageSchema), message.model_dump())
            sess.commit()

    def get_messages(
        self,
        registry: str,
        uid: str,
    ) -> List[Optional[Message]]:
        """Get messages

        Args:
            uid:
                Uid
            registry:
                Registry type
        Returns:
            List of messages
        """

        parent_query = select(MessageSchema).filter(
            MessageSchema.uid.is_(uid),
            MessageSchema.registry.is_(registry),
            MessageSchema.parent_id.is_(None),
        )

        query = parent_query.union_all(
            select(MessageSchema).filter(
                MessageSchema.uid.is_(uid),
                MessageSchema.registry.is_(registry),
                MessageSchema.parent_id.isnot(None),
            )
        )

        with self.session() as sess:
            results = sess.execute(query).all()

        if not results:
            return []

        return [Message(**row._asdict()) for row in results]

    def update_message(self, message: Message) -> None:
        """Update message

        Args:
            message:
                message record
        """
        message_uid = cast(int, message.get("message_id"))
        with self.session() as sess:
            query = sess.query(MessageSchema).filter(MessageSchema.message_id == message_uid)
            query.update(message.model_dump())  # type: ignore
            sess.commit()


def get_query_engine(db_engine: Engine, registry_type: RegistryType) -> Union[QueryEngine, ProjectQueryEngine]:
    """Get query engine based on registry type

    Args:
        db_engine:
            Database engine
        registry_type:
            Registry type
    Returns:
        Query engine
    """
    # this allows us to eventually expand into custom registry logic if we need to
    if registry_type == RegistryType.PROJECT:
        return ProjectQueryEngine(engine=db_engine)
    if registry_type == RegistryType.RUN:
        return RunQueryEngine(engine=db_engine)
    if registry_type == RegistryType.AUTH:
        return AuthQueryEngine(engine=db_engine)
    if registry_type == RegistryType.MESSAGE:
        return MessageQueryEngine(engine=db_engine)
    return QueryEngine(engine=db_engine)
