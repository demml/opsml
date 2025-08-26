# pylint: skip-file

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Protocol, TypeAlias

from ...llm import Prompt
from ...logging import LogLevel
from ...mock import MockConfig
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
        username: Optional[str] = None,
        password: Optional[str] = None,
        brokers: Optional[str] = None,
        topic: Optional[str] = None,
        compression_type: Optional[str] = None,
        message_timeout_ms: int = 600_000,
        message_max_bytes: int = 2097164,
        log_level: LogLevel = LogLevel.Info,
        config: Dict[str, str] = {},
        max_retries: int = 3,
    ) -> None:
        """Kafka configuration for connecting to and publishing messages to Kafka brokers.

        This configuration supports both authenticated (SASL) and unauthenticated connections.
        When credentials are provided, SASL authentication is automatically enabled with
        secure defaults.

        Authentication Priority (first match wins):
            1. Direct parameters (username/password)
            2. Environment variables (KAFKA_USERNAME/KAFKA_PASSWORD)
            3. Configuration dictionary (sasl.username/sasl.password)

        SASL Security Defaults:
            - security.protocol: "SASL_SSL" (override via KAFKA_SECURITY_PROTOCOL env var)
            - sasl.mechanism: "PLAIN" (override via KAFKA_SASL_MECHANISM env var)

        Args:
            username:
                SASL username for authentication.
                Fallback: KAFKA_USERNAME environment variable.
            password:
                SASL password for authentication.
                Fallback: KAFKA_PASSWORD environment variable.
            brokers:
                Comma-separated list of Kafka broker addresses (host:port).
                Fallback: KAFKA_BROKERS environment variable.
                Default: "localhost:9092"
            topic:
                Target Kafka topic for message publishing.
                Fallback: KAFKA_TOPIC environment variable.
                Default: "scouter_monitoring"
            compression_type:
                Message compression algorithm.
                Options: "none", "gzip", "snappy", "lz4", "zstd"
                Default: "gzip"
            message_timeout_ms:
                Maximum time to wait for message delivery (milliseconds).
                Default: 600000 (10 minutes)
            message_max_bytes:
                Maximum message size in bytes.
                Default: 2097164 (~2MB)
            log_level:
                Logging verbosity for the Kafka producer.
                Default: LogLevel.Info
            config:
                Additional Kafka producer configuration parameters.
                See: https://kafka.apache.org/documentation/#producerconfigs
                Note: Direct parameters take precedence over config dictionary values.
            max_retries:
                Maximum number of retry attempts for failed message deliveries.
                Default: 3

        Examples:
            Basic usage (unauthenticated):
            ```python
            config = KafkaConfig(
                brokers="kafka1:9092,kafka2:9092",
                topic="my_topic"
            )
            ```

            SASL authentication:
            ```python
            config = KafkaConfig(
                username="my_user",
                password="my_password",
                brokers="secure-kafka:9093",
                topic="secure_topic"
            )
            ```

            Advanced configuration:
            ```python
            config = KafkaConfig(
                brokers="kafka:9092",
                compression_type="lz4",
                config={
                    "acks": "all",
                    "batch.size": "32768",
                    "linger.ms": "10"
                }
            )
            ```
        """

    def __str__(self): ...

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

    def __str__(self): ...

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

    def __str__(self): ...

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
    def __init__(self, name: str, value: Any) -> None:
        """Initialize feature. Will attempt to convert the value to it's corresponding feature type.
        Current support types are int, float, string.

        Args:
            name:
                Name of the feature
            value:
                Value of the feature. Can be an int, float, or string.

        Example:
            ```python
            feature = Feature("feature_1", 1) # int feature
            feature = Feature("feature_2", 2.0) # float feature
            feature = Feature("feature_3", "value") # string feature
            ```
        """

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

    @staticmethod
    def categorical(name: str, value: str) -> "Feature":
        """Create a categorical feature

        Args:
            name:
                Name of the feature
            value:
                Value of the feature
        """

class Features:
    def __init__(
        self,
        features: List[Feature] | Dict[str, Union[int, float, str]],
    ) -> None:
        """Initialize a features class

        Args:
            features:
                List of features or a dictionary of key-value pairs.
                If a list, each item must be an instance of Feature.
                If a dictionary, each key is the feature name and each value is the feature value.
                Supported types for values are int, float, and string.

        Example:
            ```python
            # Passing a list of features
            features = Features(
                features=[
                    Feature.int("feature_1", 1),
                    Feature.float("feature_2", 2.0),
                    Feature.string("feature_3", "value"),
                ]
            )

            # Passing a dictionary (pydantic model) of features
            class MyFeatures(BaseModel):
                feature1: int
                feature2: float
                feature3: str

            my_features = MyFeatures(
                feature1=1,
                feature2=2.0,
                feature3="value",
            )

            features = Features(my_features.model_dump())
            ```
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
    def __init__(self, name: str, value: float | int) -> None:
        """Initialize metric

        Args:
            name:
                Name of the metric
            value:
                Value to assign to the metric. Can be an int or float but will be converted to float.
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
    def __init__(self, metrics: List[Metric] | Dict[str, Union[int, float]]) -> None:
        """Initialize metrics

        Args:
            metrics:
                List of metrics or a dictionary of key-value pairs.
                If a list, each item must be an instance of Metric.
                If a dictionary, each key is the metric name and each value is the metric value.


        Example:
            ```python

            # Passing a list of metrics
            metrics = Metrics(
                metrics=[
                    Metric("metric_1", 1.0),
                    Metric("metric_2", 2.5),
                    Metric("metric_3", 3),
                ]
            )

            # Passing a dictionary (pydantic model) of metrics
            class MyMetrics(BaseModel):
                metric1: float
                metric2: int

            my_metrics = MyMetrics(
                metric1=1.0,
                metric2=2,
            )

            metrics = Metrics(my_metrics.model_dump())
        """

    def __str__(self) -> str:
        """Return the string representation of the metrics"""

class Queue:
    """Individual queue associated with a drift profile"""

    def insert(self, entity: Union[Features, Metrics, LLMRecord]) -> None:
        """Insert a record into the queue

        Args:
            entity:
                Entity to insert into the queue.
                Can be an instance for Features, Metrics, or LLMRecord.

        Example:
            ```python
            features = Features(
                features=[
                    Feature("feature_1", 1),
                    Feature("feature_2", 2.0),
                    Feature("feature_3", "value"),
                ]
            )
            queue.insert(features)
            ```
        """

    @property
    def identifier(self) -> str:
        """Return the identifier of the queue"""

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
                        Feature("feature_1", 1),
                        Feature("feature_2", 2.0),
                        Feature("feature_3", "value"),
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

    @property
    def transport_config(
        self,
    ) -> Union[KafkaConfig, RabbitMQConfig, RedisConfig, HTTPConfig, MockConfig]:
        """Return the transport configuration used by the queue"""

class BaseModel(Protocol):
    """Protocol for pydantic BaseModel to ensure compatibility with context"""

    def model_dump(self) -> Dict[str, Any]:
        """Dump the model as a dictionary"""
        ...

    def model_dump_json(self) -> str:
        """Dump the model as a JSON string"""
        ...

    def __str__(self) -> str:
        """String representation of the model"""
        ...

SerializedType: TypeAlias = Union[str, int, float, dict, list]
Context: TypeAlias = Union[Dict[str, Any], BaseModel]

class LLMRecord:
    """LLM record containing context tied to a Large Language Model interaction
    that is used to evaluate drift in LLM responses.


    Examples:
        >>> record = LLMRecord(
        ...     context={
        ...         "input": "What is the capital of France?",
        ...         "response": "Paris is the capital of France."
        ...     },
        ... )
        >>> print(record.context["input"])
        "What is the capital of France?"
    """

    prompt: Optional[Prompt]
    """Optional prompt configuration associated with this record."""

    entity_type: EntityType
    """Type of entity, always EntityType.LLM for LLMRecord instances."""

    def __init__(
        self,
        context: Context,
        prompt: Optional[Prompt | SerializedType] = None,
    ) -> None:
        """Creates a new LLM record to associate with an `LLMDriftProfile`.
        The record is sent to the `Scouter` server via the `ScouterQueue` and is
        then used to inject context into the evaluation prompts.

        Args:
            context:
                Additional context information as a dictionary or a pydantic BaseModel. During evaluation,
                this will be merged with the input and response data and passed to the assigned
                evaluation prompts. So if you're evaluation prompts expect additional context via
                bound variables (e.g., `${foo}`), you can pass that here as key value pairs.
                {"foo": "bar"}
            prompt:
                Optional prompt configuration associated with this record. Can be a Potatohead Prompt or
                a JSON-serializable type.

        Raises:
            TypeError: If context is not a dict or a pydantic BaseModel.

        """
        ...

    @property
    def context(self) -> Dict[str, Any]:
        """Get the contextual information.

        Returns:
            The context data as a Python object (deserialized from JSON).

        Raises:
            TypeError: If the stored JSON cannot be converted to a Python object.
        """
        ...
