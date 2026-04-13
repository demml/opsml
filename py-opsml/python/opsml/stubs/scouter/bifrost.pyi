#### begin imports ####

from typing import Any, Dict, List, Optional, Type

#### end of imports ####

class TableConfig:
    """Configuration for a dataset table, derived from a Pydantic model.

    Eagerly computes Arrow schema, fingerprint, and namespace from the model class.

    Args:
        model: Pydantic model class (not an instance).
        catalog: Catalog name.
        schema_name: Schema name.
        table: Table name.
        partition_columns: Optional list of partition column names.
    """

    catalog: str
    schema_name: str
    table: str
    partition_columns: List[str]

    def __init__(
        self,
        model: Type[Any],
        catalog: str,
        schema_name: str,
        table: str,
        partition_columns: Optional[List[str]] = None,
    ) -> None: ...
    @property
    def fingerprint_str(self) -> str: ...
    @property
    def fqn(self) -> str: ...
    @staticmethod
    def parse_schema(schema: Any) -> Dict[str, Dict[str, Any]]:
        """Parse a Pydantic model's JSON Schema dict into a field map.

        Accepts the dict returned directly by ``Model.model_json_schema()``.

        System columns (``scouter_created_at``, ``scouter_partition_date``,
        ``scouter_batch_id``) are included automatically.

        Args:
            schema: Dict returned by ``Model.model_json_schema()``.

        Returns:
            Mapping of field name to Arrow type descriptor
            with ``arrow_type`` (str) and ``nullable`` (bool) keys.
        """

    @staticmethod
    def compute_fingerprint(schema: Any) -> str:
        """Compute a stable 32-character SHA-256 fingerprint from a JSON Schema dict.

        The fingerprint is deterministic — the same schema always yields the same value.
        Any field addition, removal, or type change yields a different value.

        Args:
            schema: Dict returned by ``Model.model_json_schema()``.

        Returns:
            32-character hexadecimal fingerprint string.
        """

class WriteConfig:
    """Configuration for dataset write behavior.

    Args:
        batch_size: Number of rows per batch (default: 1000).
        scheduled_delay_secs: Seconds between scheduled flushes (default: 30).
    """

    batch_size: int
    scheduled_delay_secs: int

    def __init__(
        self,
        batch_size: int = 1000,
        scheduled_delay_secs: int = 30,
    ) -> None: ...

class QueryResult:
    """Wrapper around Arrow IPC stream bytes returned by a SQL query.

    Provides zero-copy conversion to ``pyarrow.Table``, ``polars.DataFrame``,
    and ``pandas.DataFrame``. The IPC bytes are stored once; each conversion
    reads from the same buffer.
    """

    def to_arrow(self) -> Any:
        """Convert to a ``pyarrow.Table``. Requires ``pyarrow``."""

    def to_polars(self) -> Any:
        """Convert to a ``polars.DataFrame`` (zero-copy from Arrow).

        Requires ``polars`` and ``pyarrow``.
        """

    def to_pandas(self) -> Any:
        """Convert to a ``pandas.DataFrame``. Requires ``pyarrow``."""

    def to_bytes(self) -> bytes:
        """Get the raw Arrow IPC stream bytes."""

    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...

class DatasetClient:
    """Dataset client for reading and querying datasets.

    When ``table_config`` is provided, validates the schema fingerprint on
    construction and enables ``read()`` for Pydantic model deserialization.
    When omitted, works as a general-purpose query client: ``sql()``,
    ``list_datasets()``, and ``describe_dataset()`` all work without a table
    binding.

    Args:
        transport: gRPC transport configuration (``GrpcConfig`` instance).
        table_config: Optional table configuration. Required for ``read()``.
    """

    def __init__(self, transport: Any, table_config: Optional[TableConfig] = None) -> None: ...
    def read(self, limit: Optional[int] = None) -> List[Any]:
        """Read all rows from the bound table as Pydantic model instances.

        Uses the model class from ``TableConfig`` for validation via
        ``model.model_validate()``.

        Args:
            limit: Optional maximum number of rows to return.

        Returns:
            List of validated Pydantic model instances.
        """

    def sql(self, query: str) -> QueryResult:
        """Execute a SQL SELECT query and return a ``QueryResult``.

        The ``QueryResult`` wraps Arrow IPC stream bytes and provides
        zero-copy conversion methods.

        Args:
            query: SQL SELECT statement. Supports three-level table names
                (``catalog.schema.table``), CTEs, window functions, subqueries.

        Returns:
            A ``QueryResult`` with ``.to_arrow()``, ``.to_polars()``,
            ``.to_pandas()``, and ``.to_bytes()`` methods.
        """

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets.

        Returns:
            List of dicts with keys: ``catalog``, ``schema_name``, ``table``,
            ``fingerprint``, ``partition_columns``, ``status``,
            ``created_at``, ``updated_at``.
        """

    def describe_dataset(
        self,
        catalog: str,
        schema_name: str,
        table: str,
    ) -> Dict[str, Any]:
        """Get metadata and schema for a specific dataset.

        Args:
            catalog: Catalog name.
            schema_name: Schema name.
            table: Table name.

        Returns:
            Dict with dataset info fields and ``arrow_schema_json``.
        """

class DatasetProducer:
    """Real-time streaming producer for the Scouter dataset engine.

    Pushes Pydantic model instances through a Rust queue to Delta Lake via gRPC.
    Always has an active background queue.

    Args:
        table_config: Table configuration derived from a Pydantic model.
        transport: Transport configuration (e.g., GrpcConfig).
        write_config: Optional write configuration.
    """

    def __init__(
        self,
        table_config: TableConfig,
        transport: Any,
        write_config: Optional[WriteConfig] = None,
    ) -> None: ...
    def insert(self, record: Any) -> None:
        """Insert a Pydantic model instance into the queue.

        Calls ``record.model_dump_json()`` and sends via channel. Non-blocking.
        """

    def flush(self) -> None:
        """Signal the background queue to flush immediately."""

    def shutdown(self) -> None:
        """Gracefully shut down the producer, flushing remaining items."""

    def register(self) -> str:
        """Register the dataset table with the server.

        Optional — auto-registers on first flush if not called explicitly.

        Returns:
            Registration status from the server.
        """

    @property
    def fingerprint(self) -> str: ...
    @property
    def namespace(self) -> str: ...
    @property
    def is_registered(self) -> bool: ...

class Bifrost:
    """Unified read/write client for the Bifrost dataset engine.

    Wraps both ``DatasetProducer`` and ``DatasetClient`` into a single object.
    Use this when you need both write and read access to the same table.
    Access the underlying clients directly via ``.producer`` and ``.client``
    for the full API.

    Args:
        table_config: Table configuration derived from a Pydantic model.
        transport: gRPC transport configuration (``GrpcConfig`` instance).
        write_config: Optional write configuration for batching behavior.
    """

    def __init__(
        self,
        table_config: TableConfig,
        transport: Any,
        write_config: Optional[WriteConfig] = None,
    ) -> None: ...
    def insert(self, record: Any) -> None:
        """Insert a Pydantic model instance into the queue. Non-blocking."""

    def flush(self) -> None:
        """Signal the background queue to flush immediately."""

    def shutdown(self) -> None:
        """Gracefully shut down the producer, flushing remaining items."""

    def register(self) -> str:
        """Register the dataset table with the server."""

    @property
    def fingerprint(self) -> str: ...
    @property
    def namespace(self) -> str: ...
    @property
    def is_registered(self) -> bool: ...
    def read(self, limit: Optional[int] = None) -> List[Any]:
        """Read rows from the bound table as validated Pydantic model instances."""

    def sql(self, query: str) -> QueryResult:
        """Execute a SQL SELECT query and return a ``QueryResult``."""

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets on the server."""

    def describe_dataset(self, catalog: str, schema_name: str, table: str) -> Dict[str, Any]:
        """Get metadata and schema for a specific dataset."""

    @property
    def producer(self) -> DatasetProducer:
        """The underlying ``DatasetProducer`` for full write API access."""

    @property
    def client(self) -> DatasetClient:
        """The underlying ``DatasetClient`` for full read API access."""

__all__ = [
    "Bifrost",
    "DatasetClient",
    "DatasetProducer",
    "QueryResult",
    "TableConfig",
    "WriteConfig",
]
