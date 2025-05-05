# pylint: skip-file

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...logging import LogLevel
from ..client import HTTPConfig
from ..observe import ObservabilityMetrics

class TransportType:
    Kafka = "TransportType"
    RabbitMQ = "TransportType"
    Redis = "TransportType"
    HTTP = "TransportType"

class EntityType:
    Feature = "EntityType"
    Metric = "EntityType"

class RecordType:
    Spc = "RecordType"
    Psi = "RecordType"
    Observability = "RecordType"
    Custom = "RecordType"

class KafkaConfig:
    brokers: str
    topic: str
    compression_type: str
    message_timeout_ms: int
    message_max_bytes: int
    log_level: LogLevel
    config: Dict[str, str]
    max_retries: int
    transport_type: TransportType

    def __init__(
        self,
        brokers: Optional[str] = None,
        topic: Optional[str] = None,
        compression_type: Optional[str] = None,
        message_timeout_ms: int = 600_000,
        message_max_bytes: int = 2097164,
        log_level: LogLevel = LogLevel.Info,
        config: Dict[str, str] = {},
        max_retries: int = 3,
    ) -> None:
        """Kafka configuration to use with the KafkaProducer.

        Args:
            brokers:
                Comma-separated list of Kafka brokers.
                If not provided, the value of the KAFKA_BROKERS environment variable is used.

            topic:
                Kafka topic to publish messages to.
                If not provided, the value of the KAFKA_TOPIC environment variable is used.

            compression_type:
                Compression type to use for messages.
                Default is "gzip".

            message_timeout_ms:
                Message timeout in milliseconds.
                Default is 600_000.

            message_max_bytes:
                Maximum message size in bytes.
                Default is 2097164.

            log_level:
                Log level for the Kafka producer.
                Default is LogLevel.Info.

            config:
                Additional Kafka configuration options. These will be passed to the Kafka producer.
                See https://kafka.apache.org/documentation/#configuration.

            max_retries:
                Maximum number of retries to attempt when publishing messages.
                Default is 3.

        """

class RabbitMQConfig:
    address: str
    queue: str
    max_retries: int
    transport_type: TransportType

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        queue: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """RabbitMQ configuration to use with the RabbitMQProducer.

        Args:
            host:
                RabbitMQ host.
                If not provided, the value of the RABBITMQ_HOST environment variable is used.

            port:
                RabbitMQ port.
                If not provided, the value of the RABBITMQ_PORT environment variable is used.

            username:
                RabbitMQ username.
                If not provided, the value of the RABBITMQ_USERNAME environment variable is used.

            password:
                RabbitMQ password.
                If not provided, the value of the RABBITMQ_PASSWORD environment variable is used.

            queue:
                RabbitMQ queue to publish messages to.
                If not provided, the value of the RABBITMQ_QUEUE environment variable is used.

            max_retries:
                Maximum number of retries to attempt when publishing messages.
                Default is 3.
        """

class RedisConfig:
    address: str
    channel: str
    transport_type: TransportType

    def __init__(
        self,
        address: Optional[str] = None,
        chanel: Optional[str] = None,
    ) -> None:
        """Redis configuration to use with a Redis producer

        Args:
            address (str):
                Redis address.
                If not provided, the value of the REDIS_ADDR environment variable is used and defaults to "redis://localhost:6379".

            channel (str):
                Redis channel to publish messages to.
                If not provided, the value of the REDIS_CHANNEL environment variable is used and defaults to "scouter_monitoring".
        """

class ServerRecord:
    Spc: "ServerRecord"
    Psi: "ServerRecord"
    Custom: "ServerRecord"
    Observability: "ServerRecord"

    def __init__(self, record: Any) -> None:
        """Initialize server record

        Args:
            record:
                Server record to initialize
        """

    @property
    def record(
        self,
    ) -> Union[SpcServerRecord, PsiServerRecord, CustomMetricServerRecord, ObservabilityMetrics]:
        """Return the drift server record."""

class ServerRecords:
    def __init__(self, records: List[ServerRecord]) -> None:
        """Initialize server records

        Args:
            records:
                List of server records
        """

    @property
    def records(self) -> List[ServerRecord]:
        """Return the drift server records."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

class SpcServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        feature: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            feature:
                Feature name
            value:
                Feature value
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

    @property
    def feature(self) -> str:
        """Return the feature."""

    @property
    def value(self) -> float:
        """Return the sample value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class PsiServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        feature: str,
        bin_id: int,
        bin_count: int,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            feature:
                Feature name
            bin_id:
                Bundle ID
            bin_count:
                Bundle ID
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

    @property
    def feature(self) -> str:
        """Return the feature."""

    @property
    def bin_id(self) -> int:
        """Return the bin id."""

    @property
    def bin_count(self) -> int:
        """Return the sample value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class CustomMetricServerRecord:
    def __init__(
        self,
        space: str,
        name: str,
        version: str,
        metric: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            metric:
                Metric name
            value:
                Metric value
        """

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp."""

    @property
    def space(self) -> str:
        """Return the space."""

    @property
    def name(self) -> str:
        """Return the name."""

    @property
    def version(self) -> str:
        """Return the version."""

    @property
    def metric(self) -> str:
        """Return the metric name."""

    @property
    def value(self) -> float:
        """Return the metric value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class Feature:
    @staticmethod
    def int(name: str, value: int) -> "Feature":
        """Create an integer feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def float(name: str, value: float) -> "Feature":
        """Create a float feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

    @staticmethod
    def string(name: str, value: str) -> "Feature":
        """Create a string feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

class Features:
    def __init__(self, features: List[Feature]) -> None:
        """Initialize features

        Args:
            features:
                List of features
        """

    def __str__(self) -> str:
        """Return the string representation of the features"""

    @property
    def features(self) -> List[Feature]:
        """Return the list of features"""

    @property
    def entity_type(self) -> EntityType:
        """Return the entity type"""

class Metric:
    def __init__(self, name: str, value: float) -> None:
        """Initialize metric

        Args:
            name:
                Name of the metric
            value:
                Value to assign to the metric
        """

    def __str__(self) -> str:
        """Return the string representation of the metric"""

    @property
    def metrics(self) -> List[Metric]:
        """Return the list of metrics"""

    @property
    def entity_type(self) -> EntityType:
        """Return the entity type"""

class Metrics:
    def __init__(self, metrics: List[Metric]) -> None:
        """Initialize metrics

        Args:
            metrics:
                List of metrics
        """

    def __str__(self) -> str:
        """Return the string representation of the metrics"""

class Queue:
    """Individual queue associated with a drift profile"""

    def insert(self, entity: Union[Features, Metrics]) -> None:
        """Insert a record into the queue

        Args:
            entity:
                Entity to insert into the queue.
                Can be an instance for Features or Metrics

        Example:
            ```python
            features = Features(
                features=[
                    Feature.int("feature_1", 1),
                    Feature.float("feature_2", 2.0),
                    Feature.string("feature_3", "value"),
                ]
            )
            queue.insert(Features(features))
            ```
        """

class ScouterQueue:
    """Main queue class for Scouter. Publishes drift records to the configured transport"""

    @staticmethod
    def from_path(
        path: Dict[str, Path],
        transport_config: Union[
            KafkaConfig,
            RabbitMQConfig,
            RedisConfig,
            HTTPConfig,
        ],
    ) -> ScouterQueue:
        """Initializes Scouter queue from one or more drift profile paths

        Args:
            path (Dict[str, Path]):
                Dictionary of drift profile paths.
                Each key is a user-defined alias for accessing a queue
            transport_config (Union[KafkaConfig, RabbitMQConfig, RedisConfig, HTTPConfig]):
                Transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HTTPConfig

        Example:
            ```python
            queue = ScouterQueue(
                path={
                    "spc": Path("spc_profile.json"),
                    "psi": Path("psi_profile.json"),
                },
                transport_config=KafkaConfig(
                    brokers="localhost:9092",
                    topic="scouter_topic",
                ),
            )

            queue["psi"].insert(
                Features(
                    features=[
                        Feature.int("feature_1", 1),
                        Feature.float("feature_2", 2.0),
                        Feature.string("feature_3", "value"),
                    ]
                )
            )
            ```
        """

    def __getitem__(self, key: str) -> Queue:
        """Get the queue for the specified key

        Args:
            key (str):
                Key to get the queue for

        """

    def shutdown(self) -> None:
        """Shutdown the queue. This will close and flush all queues and transports"""
