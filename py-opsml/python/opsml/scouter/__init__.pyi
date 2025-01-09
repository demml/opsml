# pylint: disable=invalid-name, too-many-lines

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from numpy.typing import NDArray

class DriftType:
    Spc: "DriftType"
    Psi: "DriftType"
    Custom: "DriftType"

    def value(self) -> str: ...
    @staticmethod
    def from_value(value: str) -> "DriftType": ...

class RecordType:
    Spc = "RecordType"
    Psi = "RecordType"
    Observability = "RecordType"
    Custom = "RecordType"

class SpcServerRecord:
    def __init__(
        self,
        repository: str,
        name: str,
        version: str,
        feature: str,
        value: float,
    ):
        """Initialize spc drift server record

        Args:
            repository:
                Model repository
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
    def repository(self) -> str:
        """Return the repository."""

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
    ) -> Union[
        SpcServerRecord, PsiServerRecord, CustomMetricServerRecord, ObservabilityMetrics
    ]:
        """Return the drift server record."""

class ServerRecords:
    def __init__(self, records: List[ServerRecord], record_type: RecordType) -> None:
        """Initialize server records

        Args:
            records:
                List of server records
            record_type:
                Type of server records
        """

    @property
    def record_type(self) -> RecordType:
        """Return the drift type."""

    @property
    def records(self) -> List[ServerRecord]:
        """Return the drift server records."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

class Every1Minute:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class Every5Minutes:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class Every15Minutes:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class Every30Minutes:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class EveryHour:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class Every6Hours:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class Every12Hours:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class EveryDay:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class EveryWeek:
    def __init__(self) -> None:
        """Initialize the cron schedule"""

    @property
    def cron(self) -> str:
        """Return the cron schedule"""

class CommonCron:
    def __init__(self) -> None:
        """Initialize the common cron class from rust"""

    @property
    def EVERY_1_MINUTE(self) -> str:
        """Every 1 minute cron schedule"""

    @property
    def EVERY_5_MINUTES(self) -> str:
        """Every 5 minutes cron schedule"""

    @property
    def EVERY_15_MINUTES(self) -> str:
        """Every 15 minutes cron schedule"""

    @property
    def EVERY_30_MINUTES(self) -> str:
        """Every 30 minutes cron schedule"""

    @property
    def EVERY_HOUR(self) -> str:
        """Every hour cron schedule"""

    @property
    def EVERY_6_HOURS(self) -> str:
        """Every 6 hours cron schedule"""

    @property
    def EVERY_12_HOURS(self) -> str:
        """Every 12 hours cron schedule"""

    @property
    def EVERY_DAY(self) -> str:
        """Every day cron schedule"""

    @property
    def EVERY_WEEK(self) -> str:
        """Every week cron schedule"""

class AlertZone:
    Zone1: "AlertZone"
    Zone2: "AlertZone"
    Zone3: "AlertZone"
    Zone4: "AlertZone"
    NotApplicable: "AlertZone"

class SpcAlertType:
    OutOfBounds = "SpcAlertType"
    Consecutive = "SpcAlertType"
    Alternating = "SpcAlertType"
    AllGood = "SpcAlertType"
    Trend = "SpcAlertType"

class SpcAlertRule:
    def __init__(
        self,
        rule: Optional[str] = None,
        zones_to_monitor: Optional[List[AlertZone]] = None,
    ) -> None:
        """Initialize alert rule

        Args:
            rule:
                Rule to use for alerting. Eight digit integer string.
                Defaults to '8 16 4 8 2 4 1 1'
            zones_to_monitor:
                List of zones to monitor. Defaults to all zones.
        """

    @property
    def rule(self) -> str:
        """Return the alert rule"""

    @rule.setter
    def rule(self, rule: str) -> None:
        """Set the alert rule"""

    @property
    def zones_to_monitor(self) -> List[AlertZone]:
        """Return the zones to monitor"""

    @zones_to_monitor.setter
    def zones_to_monitor(self, zones_to_monitor: List[AlertZone]) -> None:
        """Set the zones to monitor"""

class AlertDispatchType:
    Email: "AlertDispatchType"
    Console: "AlertDispatchType"
    Slack: "AlertDispatchType"
    OpsGenie: "AlertDispatchType"

class PsiAlertConfig:
    def __init__(
        self,
        dispatch_type: Optional[AlertDispatchType] = None,
        schedule: Optional[str] = None,
        features_to_monitor: Optional[List[str]] = None,
        dispatch_kwargs: Optional[Dict[str, Any]] = None,
        psi_threshold: Optional[float] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_type:
                Alert dispatch type to use. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features
            dispatch_kwargs:
                Additional alert kwargs to pass to the alerting service

                Supported alert_kwargs:
                Slack:
                    - channel: str (channel to send slack message)
                OpsGenie:
                    - team: str (team to send opsgenie message)
                    - priority: str (priority for opsgenie alerts)
            psi_threshold:
                What threshold must be met before sending alert messages default is 0.25

        """

    @property
    def dispatch_type(self) -> str:
        """Return the alert dispatch type"""

    @dispatch_type.setter
    def dispatch_type(self, alert_dispatch_type: str) -> None:
        """Set the alert dispatch type"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def features_to_monitor(self) -> List[str]:
        """Return the features to monitor"""

    @features_to_monitor.setter
    def features_to_monitor(self, features_to_monitor: List[str]) -> None:
        """Set the features to monitor"""

    @property
    def dispatch_kwargs(self) -> Dict[str, Any]:
        """Return the dispatch kwargs"""

    @dispatch_kwargs.setter
    def dispatch_kwargs(self, dispatch_kwargs: Dict[str, Any]) -> None:
        """Set the dispatch kwargs"""

    @property
    def psi_threshold(self) -> float:
        """Return the schedule"""

    @psi_threshold.setter
    def psi_threshold(self, threshold: float) -> None:
        """Set the schedule"""

class SpcAlertConfig:
    def __init__(
        self,
        rule: Optional[SpcAlertRule] = None,
        dispatch_type: Optional[AlertDispatchType] = None,
        schedule: Optional[str] = None,
        features_to_monitor: Optional[List[str]] = None,
        dispatch_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize alert config

        Args:
            rule:
                Alert rule to use. Defaults to Standard
            dispatch_type:
                Alert dispatch type to use. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features
            dispatch_kwargs:
                Additional alert kwargs to pass to the alerting service

                Supported alert_kwargs:
                Slack:
                    - channel: str (channel to send slack message)
                OpsGenie:
                    - team: str (team to send opsgenie message)
                    - priority: str (priority for opsgenie alerts)

        """

    @property
    def dispatch_type(self) -> str:
        """Return the alert dispatch type"""

    @dispatch_type.setter
    def dispatch_type(self, alert_dispatch_type: str) -> None:
        """Set the alert dispatch type"""

    @property
    def rule(self) -> SpcAlertRule:
        """Return the alert rule"""

    @rule.setter
    def rule(self, rule: SpcAlertRule) -> None:
        """Set the alert rule"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def features_to_monitor(self) -> List[str]:
        """Return the features to monitor"""

    @features_to_monitor.setter
    def features_to_monitor(self, features_to_monitor: List[str]) -> None:
        """Set the features to monitor"""

    @property
    def dispatch_kwargs(self) -> Dict[str, Any]:
        """Return the dispatch kwargs"""

    @dispatch_kwargs.setter
    def dispatch_kwargs(self, dispatch_kwargs: Dict[str, Any]) -> None:
        """Set the dispatch kwargs"""

class SpcAlert:
    def __init__(self, kind: SpcAlertType, zone: AlertZone):
        """Initialize alert"""

    @property
    def kind(self) -> SpcAlertType:
        """Alert kind"""

    @property
    def zone(self) -> AlertZone:
        """Zone associated with alert"""

    def __str__(self) -> str:
        """Return the string representation of the alert."""

class SpcFeatureAlert:
    @property
    def feature(self) -> str:
        """Return the feature."""

    @property
    def alerts(self) -> List[SpcAlert]:
        """Return the alerts."""

class SpcFeatureAlerts:
    @property
    def features(self) -> Dict[str, SpcFeatureAlert]:
        """Return the feature alerts."""

    @property
    def has_alerts(self) -> bool:
        """Returns true if there are alerts"""

class FeatureMap:
    @property
    def features(self) -> Dict[str, Dict[str, int]]:
        """Return the feature map."""

    def __str__(self) -> str:
        """Return the string representation of the feature map."""

class SpcFeatureDriftProfile:
    @property
    def id(self) -> str:
        """Return the id."""

    @property
    def center(self) -> float:
        """Return the center."""

    @property
    def one_ucl(self) -> float:
        """Return the zone 1 ucl."""

    @property
    def one_lcl(self) -> float:
        """Return the zone 1 lcl."""

    @property
    def two_ucl(self) -> float:
        """Return the zone 2 ucl."""

    @property
    def two_lcl(self) -> float:
        """Return the zone 2 lcl."""

    @property
    def three_ucl(self) -> float:
        """Return the zone 3 ucl."""

    @property
    def three_lcl(self) -> float:
        """Return the zone 3 lcl."""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

class PsiDriftConfig:
    def __init__(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[PsiAlertConfig] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        config_path: Optional[Path] = None,
    ):
        """Initialize monitor config

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
            config_path:
                Optional path to load config from.
        """

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def repository(self) -> str:
        """Model repository"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set model repository"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @feature_map.setter
    def feature_map(self, feature_map: FeatureMap) -> None:
        """Set feature map"""

    @property
    def targets(self) -> List[str]:
        """List of target features to monitor"""

    @targets.setter
    def targets(self, targets: List[str]) -> None:
        """Set list of target features to monitor"""

    @property
    def alert_config(self) -> PsiAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: PsiAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    def update_feature_map(self, feature_map: FeatureMap) -> None:
        """Update feature map"""

    @staticmethod
    def load_from_json_file(path: Path) -> "PsiDriftConfig":
        """Load config from json file

        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        alert_config: Optional[PsiAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
        """

class SpcDriftConfig:
    def __init__(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample: bool = True,
        sample_size: int = 25,
        alert_config: Optional[SpcAlertConfig] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        config_path: Optional[Path] = None,
    ):
        """Initialize monitor config

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            sample:
                Whether to sample or not
            sample_size:
                Sample size
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
            config_path:
                Optional path to load config from.
        """

    @property
    def sample_size(self) -> int:
        """Return the sample size."""

    @sample_size.setter
    def sample_size(self, sample_size: int) -> None:
        """Set the sample size."""

    @property
    def sample(self) -> bool:
        """Whether to sample or not"""

    @sample.setter
    def sample(self, sample: bool) -> None:
        """Set whether to sample or not"""

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def repository(self) -> str:
        """Model repository"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set model repository"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @feature_map.setter
    def feature_map(self, feature_map: FeatureMap) -> None:
        """Set feature map"""

    @property
    def targets(self) -> List[str]:
        """List of target features to monitor"""

    @targets.setter
    def targets(self, targets: List[str]) -> None:
        """Set list of target features to monitor"""

    @property
    def alert_config(self) -> SpcAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: SpcAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    def update_feature_map(self, feature_map: FeatureMap) -> None:
        """Update feature map"""

    @staticmethod
    def load_from_json_file(path: Path) -> "SpcDriftConfig":
        """Load config from json file

        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample: Optional[bool] = None,
        sample_size: Optional[int] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            sample:
                Whether to sample or not
            sample_size:
                Sample size
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
        """

class SpcDriftProfile:
    def __init__(
        self,
        features: Dict[str, SpcFeatureDriftProfile],
        config: SpcDriftConfig,
        scouter_version: Optional[str] = None,
    ):
        """Initialize drift profile

        Args:
            features:
                Dictionary of features and their drift profiles
            config:
                Monitor config
            scouter_version:
                version of scouter used to generate profile
        """

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, SpcFeatureDriftProfile]:
        """Return the list of features."""

    @features.setter
    def features(self, features: Dict[str, SpcFeatureDriftProfile]) -> None:
        """Set the list of features."""

    @property
    def config(self) -> SpcDriftConfig:
        """Return the monitor config."""

    @config.setter
    def config(self, config: SpcDriftConfig) -> None:
        """Set the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to "drift_profile.json.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "SpcDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample: Optional[bool] = None,
        sample_size: Optional[int] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            repository:
                Model repository
            version:
                Model version
            sample:
                Whether to sample or not
            sample_size:
                Sample size
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

class Distinct:
    @property
    def count(self) -> int:
        """total unqiue value counts"""

    @property
    def percent(self) -> float:
        """percent value uniqueness"""

class Quantiles:
    @property
    def q25(self) -> float:
        """25th quantile"""

    @property
    def q50(self) -> float:
        """50th quantile"""

    @property
    def q75(self) -> float:
        """75th quantile"""

    @property
    def q99(self) -> float:
        """99th quantile"""

class Histogram:
    @property
    def bins(self) -> List[float]:
        """Bin values"""

    @property
    def bin_counts(self) -> List[int]:
        """Bin counts"""

class NumericStats:
    @property
    def mean(self) -> float:
        """Return the mean."""

    @property
    def stddev(self) -> float:
        """Return the stddev."""

    @property
    def min(self) -> float:
        """Return the min."""

    @property
    def max(self) -> float:
        """Return the max."""

    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def quantiles(self) -> Quantiles:
        """Value quantiles"""

    @property
    def histogram(self) -> Histogram:
        """Value histograms"""

class CharStats:
    @property
    def min_length(self) -> int:
        """Minimum string length"""

    @property
    def max_length(self) -> int:
        """Maximum string length"""

    @property
    def median_length(self) -> int:
        """Median string length"""

    @property
    def mean_length(self) -> float:
        """Mean string length"""

class WordStats:
    @property
    def words(self) -> Dict[str, Distinct]:
        """Distinct word counts"""

class StringStats:
    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def char_stats(self) -> CharStats:
        """Character statistics"""

    @property
    def word_stats(self) -> WordStats:
        """word statistics"""

class FeatureProfile:
    @property
    def id(self) -> str:
        """Return the id."""

    @property
    def numeric_stats(self) -> Optional[NumericStats]:
        """Return the numeric stats."""

    @property
    def string_stats(self) -> Optional[StringStats]:
        """Return the string stats."""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

    @property
    def correlations(self) -> Optional[Dict[str, float]]:
        """Feature correlation values"""

    def __str__(self) -> str:
        """Return the string representation of the feature profile."""

class DataProfile:
    """Data profile of features"""

    @property
    def features(self) -> Dict[str, FeatureProfile]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of the data profile"""

    def model_dump_json(self) -> str:
        """Return json representation of data profile"""

    @staticmethod
    def model_validate_json(json_string: str) -> "DataProfile":
        """Load Data profile from json

        Args:
            json_string:
                JSON string representation of the data profile
        """

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save data profile to json file

        Args:
            path:
                Optional path to save the data profile. If None, outputs to "data_profile.json.

        """

class FeatureDrift:
    @property
    def samples(self) -> List[float]:
        """Return list of samples"""

    @property
    def drift(self) -> List[float]:
        """Return list of drift values"""

    def __str__(self) -> str:
        """Return string representation of feature drift"""

class SpcFeatureDrift:
    @property
    def samples(self) -> List[float]:
        """Return list of samples"""

    @property
    def drift(self) -> List[float]:
        """Return list of drift values"""

class SpcDriftMap:
    """Drift map of features"""

    def __init__(self, repository: str, name: str, version: str) -> None:
        """Initialize data profile

        Args:
            service_name:
                Optional name of service associated with drift map
        """

    @property
    def repository(self) -> str:
        """Repository to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, FeatureDrift]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of data drift"""

    def model_dump_json(self) -> str:
        """Return json representation of data drift"""

    def add_feature(self, feature: str, drift: SpcFeatureDrift) -> None:
        """Add feature drift profile to drift map

        Args:
            feature:
                Name of feature
            drift:
                Feature drift
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftMap":
        """Load drift map from json file.

        Args:
            json_string:
                JSON string representation of the drift map
        """

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to "drift_map.json.

        """

    def to_numpy(self) -> Tuple[NDArray, NDArray, List[str]]:
        """Return drift map as a a tuple of sample_array, drift_array and list of features"""

class SpcDrifter:
    def __init__(self) -> None:
        """Instantiate Rust ScouterMonitor class that is
        used to create monitoring profiles and compute drifts.
        """

    def convert_strings_to_numpy_f32(
        self,
        features: List[str],
        array: List[List[str]],
        drift_profile: SpcDriftProfile,
    ) -> NDArray[Any]:
        """Convert string array to numpy f32 array

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to convert.
            drift_profile:
                Monitoring profile.
        """

    def convert_strings_to_numpy_f64(
        self,
        features: List[str],
        array: List[List[str]],
        drift_profile: SpcDriftProfile,
    ) -> NDArray[Any]:
        """Convert string array to numpy f64 array

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to convert.
            drift_profile:
                Monitoring profile.
        """

    def create_string_drift_profile(
        self,
        array: List[List[str]],
        drift_config: SpcDriftConfig,
        features: List[str],
    ) -> SpcDriftProfile:
        """Create a monitoring profile from a f32 numpy array.

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to profile.
            drift_config:
                Monitor config.

        Returns:
            Monitoring profile.
        """

    def create_numeric_drift_profile_f32(
        self,
        array: NDArray,
        features: List[str],
        drift_config: SpcDriftConfig,
    ) -> SpcDriftProfile:
        """Create a monitoring profile from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_config:
                Monitor config.

        Returns:
            Monitoring profile.
        """

    def create_numeric_drift_profile_f64(
        self,
        array: NDArray,
        features: List[str],
        drift_config: SpcDriftConfig,
    ) -> SpcDriftProfile:
        """Create a monitoring profile from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_config:
                monitor config.

        Returns:
            Monitoring profile.
        """

    def compute_drift_f32(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: SpcDriftProfile,
    ) -> SpcDriftMap:
        """Compute drift from a f32 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.


        Returns:
            DriftMap
        """

    def compute_drift_f64(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: SpcDriftProfile,
    ) -> SpcDriftMap:
        """Compute drift from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.


        Returns:
            DriftMap.
        """

    def generate_alerts(
        self,
        drift_array: NDArray,
        features: List[str],
        alert_rule: SpcAlertRule,
    ) -> SpcFeatureAlerts:
        """Generate alerts from a drift array and feature list

        Args:
            drift_array:
                Numpy array of drift values.
            features:
                List of feature names. Must match drift array.
            alert_rule:
                Alert rule to use.

        Returns:
            List of alerts.
        """

    def sample_data_f32(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: SpcDriftProfile,
    ) -> ServerRecords:
        """Sample data from a f32 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.

        Returns:
            List of server records
        """

    def sample_data_f64(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: SpcDriftProfile,
    ) -> ServerRecords:
        """Sample data from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.

        Returns:
            List of server records
        """

class PsiDriftProfile:
    def __init__(
        self,
        features: Dict[str, PsiFeatureDriftProfile],
        config: PsiDriftConfig,
        scouter_version: Optional[str] = None,
    ):
        """Initialize drift profile

        Args:
            features:
                Dictionary of features and their drift profiles
            config:
                Monitor config
            scouter_version:
                version of scouter used to generate profile
        """

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, PsiFeatureDriftProfile]:
        """Return the list of features."""

    @features.setter
    def features(self, features: Dict[str, PsiFeatureDriftProfile]) -> None:
        """Set the list of features."""

    @property
    def config(self) -> PsiDriftConfig:
        """Return the monitor config."""

    @config.setter
    def config(self, config: PsiDriftConfig) -> None:
        """Set the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to "drift_profile.json.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PsiDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "PsiDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        feature_map: Optional[FeatureMap] = None,
        targets: Optional[List[str]] = None,
        alert_config: Optional[PsiAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            repository:
                Model repository
            version:
                Model version
            feature_map:
                Feature map
            targets:
                List of features that are targets in your dataset.
                This is typically the name of your dependent variable(s).
                This primarily used for monitoring and UI purposes.
            alert_config:
                Alert configuration
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

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

class PsiFeatureQueue:
    def __init__(self, drift_profile: PsiDriftProfile) -> None:
        """Initialize the feature queue

        Args:
            drift_profile:
                Drift profile to use for feature queue.
        """

    def insert(self, features: Features) -> None:
        """Insert data into the feature queue
        Args:
            features:
                List of features to insert into the monitoring queue.
        """

    def is_empty(self) -> bool:
        """check if queue is empty
        Returns:
            bool
        """

    def clear_queue(self) -> None:
        """Clears the feature queue"""

    def create_drift_records(self) -> ServerRecords:
        """Create drift server record from data


        Returns:
            `DriftServerRecord`
        """

class SpcFeatureQueue:
    def __init__(self, drift_profile: SpcDriftProfile) -> None:
        """Initialize the feature queue

        Args:
            drift_profile:
                Drift profile to use for feature queue.
        """

    def insert(self, features: Features) -> None:
        """Insert data into the feature queue

        Args:
            features:
                List of features to insert into the monitoring queue.
        """

    def create_drift_records(self) -> ServerRecords:
        """Create drift server record from data


        Returns:
            `DriftServerRecord`
        """

    def clear_queue(self) -> None:
        """Clears the feature queue"""

class LatencyMetrics:
    @property
    def p5(self) -> float:
        """5th percentile"""

    @property
    def p25(self) -> float:
        """25th percentile"""

    @property
    def p50(self) -> float:
        """50th percentile"""

    @property
    def p95(self) -> float:
        """95th percentile"""

    @property
    def p99(self) -> float:
        """99th percentile"""

class RouteMetrics:
    @property
    def route_name(self) -> str:
        """Return the route name"""

    @property
    def metrics(self) -> LatencyMetrics:
        """Return the repository"""

    @property
    def request_count(self) -> int:
        """Request count"""

    @property
    def error_count(self) -> int:
        """Error count"""

    @property
    def error_latency(self) -> float:
        """Error latency"""

    @property
    def status_codes(self) -> Dict[int, int]:
        """Dictionary of status codes and counts"""

class ObservabilityMetrics:
    @property
    def repository(self) -> str:
        """Return the repository"""

    @property
    def name(self) -> str:
        """Return the name"""

    @property
    def version(self) -> str:
        """Return the version"""

    @property
    def request_count(self) -> int:
        """Request count"""

    @property
    def error_count(self) -> int:
        """Error count"""

    @property
    def route_metrics(self) -> List[RouteMetrics]:
        """Route metrics object"""

    def __str__(self) -> str:
        """Return the string representation of the observability metrics"""

    def model_dump_json(self) -> str:
        """Return the json representation of the observability metrics"""

class Observer:
    def __init__(self, repository: str, name: str, version: str) -> None:
        """Initializes an api metric observer

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
        """

    def increment(self, route: str, latency: float, status_code: int) -> None:
        """Increment the feature value

        Args:
            route:
                Route name
            latency:
                Latency of request
            status_code:
                Status code of request
        """

    def collect_metrics(self) -> Optional[ServerRecords]:
        """Collect metrics from observer"""

    def reset_metrics(self) -> None:
        """Reset the observer metrics"""

class Bin:
    @property
    def id(self) -> int:
        """Return the bin id."""

    @property
    def lower_limit(self) -> float:
        """Return the lower limit of the bin."""

    @property
    def upper_limit(self) -> Optional[float]:
        """Return the upper limit of the bin."""

    @property
    def proportion(self) -> float:
        """Return the proportion of data found in the bin."""

class PsiFeatureDriftProfile:
    @property
    def id(self) -> str:
        """Return the feature name"""

    @property
    def bins(self) -> List[Bin]:
        """Return the bins"""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

class PsiDriftMap:
    """Drift map of features"""

    def __init__(self, repository: str, name: str, version: str) -> None:
        """Initialize data profile

        Args:
            service_name:
                Optional name of service associated with drift map
        """

    @property
    def repository(self) -> str:
        """Repository to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, float]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of data drift"""

    def model_dump_json(self) -> str:
        """Return json representation of data drift"""

    @staticmethod
    def model_validate_json(json_string: str) -> "PsiDriftMap":
        """Load drift map from json file.

        Args:
            json_string:
                JSON string representation of the drift map
        """

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to "drift_map.json.

        """

class PsiDrifter:
    def __init__(self) -> None:
        """Instantiate Rust ScouterMonitor class that is
        used to create monitoring profiles and compute drifts.
        """

    def convert_strings_to_numpy_f32(
        self,
        features: List[str],
        array: List[List[str]],
        drift_profile: PsiDriftProfile,
    ) -> NDArray[Any]:
        """Convert string array to numpy f32 array

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to convert.
            drift_profile:
                Monitoring profile.
        """

    def convert_strings_to_numpy_f64(
        self,
        features: List[str],
        array: List[List[str]],
        drift_profile: PsiDriftProfile,
    ) -> NDArray[Any]:
        """Convert string array to numpy f64 array

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to convert.
            drift_profile:
                Monitoring profile.
        """

    def create_string_drift_profile(
        self,
        array: List[List[str]],
        drift_config: PsiDriftConfig,
        features: List[str],
    ) -> PsiDriftProfile:
        """Create a monitoring profile from a f32 numpy array.

        Args:
            features:
                List of feature names.
            array:
                List of string arrays to profile.
            drift_config:
                Monitor config.

        Returns:
            Monitoring profile.
        """

    def create_numeric_drift_profile_f32(
        self,
        array: NDArray,
        features: List[str],
        drift_config: PsiDriftConfig,
    ) -> PsiDriftProfile:
        """Create a monitoring profile from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_config:
                Monitor config.

        Returns:
            Monitoring profile.
        """

    def create_numeric_drift_profile_f64(
        self,
        array: NDArray,
        features: List[str],
        drift_config: PsiDriftConfig,
    ) -> PsiDriftProfile:
        """Create a monitoring profile from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_config:
                monitor config.

        Returns:
            Monitoring profile.
        """

    def compute_drift_f32(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: PsiDriftProfile,
    ) -> PsiDriftMap:
        """Compute drift from a f32 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.


        Returns:
            DriftMap
        """

    def compute_drift_f64(
        self,
        array: NDArray,
        features: List[str],
        drift_profile: PsiDriftProfile,
    ) -> PsiDriftMap:
        """Compute drift from a f64 numpy array.

        Args:
            features:
                List of feature names.
            array:
                Numpy array to profile.
            drift_profile:
                Monitoring profile.


        Returns:
            DriftMap.
        """

class PsiServerRecord:
    def __init__(
        self,
        repository: str,
        name: str,
        version: str,
        feature: str,
        bin_id: str,
        bin_count: int,
    ):
        """Initialize spc drift server record

        Args:
            repository:
                Model repository
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
    def repository(self) -> str:
        """Return the repository."""

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
    def bin_id(self) -> str:
        """Return the sample value."""

    @property
    def bin_count(self) -> int:
        """Return the sample value."""

    def __str__(self) -> str:
        """Return the string representation of the record."""

    def model_dump_json(self) -> str:
        """Return the json representation of the record."""

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary representation of the record."""

class AlertThreshold:
    """
    Enum representing different alert conditions for monitoring metrics.

    Attributes:
        BELOW: Indicates that an alert should be triggered when the metric is below a threshold.
        ABOVE: Indicates that an alert should be triggered when the metric is above a threshold.
        OUTSIDE: Indicates that an alert should be triggered when the metric is outside a specified range.
    """

    Below: "AlertThreshold"
    Above: "AlertThreshold"
    Outside: "AlertThreshold"

    @staticmethod
    def from_value(value: str) -> "AlertThreshold":
        """
        Creates an AlertThreshold enum member from a string value.

        Args:
            value (str): The string representation of the alert condition.

        Returns:
            AlertThreshold: The corresponding AlertThreshold enum member.
        """

class CustomMetricAlertCondition:
    def __init__(
        self,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float],
    ):
        """Initialize a CustomMetricAlertCondition instance.
        Args:
            alert_threshold (AlertThreshold): The condition that determines when an alert
                should be triggered. This could be comparisons like 'greater than',
                'less than', 'equal to', etc.
            alert_threshold_value (Optional[float], optional): A numerical boundary used in
                conjunction with the alert_threshold. This can be None for certain
                types of comparisons that don't require a fixed boundary.
        Example:
            alert_threshold = CustomMetricAlertCondition(AlertCondition.BELOW, 2.0)
        """

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @alert_threshold.setter
    def alert_threshold(self, alert_threshold: AlertThreshold) -> None:
        """Set the alert_threshold"""

    @property
    def alert_threshold_value(self) -> float:
        """Return the alert_threshold_value"""

    @alert_threshold_value.setter
    def alert_threshold_value(self, alert_threshold_value: float) -> None:
        """Set the alert_threshold_value"""

class CustomMetricAlertConfig:
    def __init__(
        self,
        dispatch_type: Optional[AlertDispatchType] = None,
        schedule: Optional[str] = None,
        dispatch_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_type:
                Alert dispatch type to use. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            dispatch_kwargs:
                Additional alert kwargs to pass to the alerting service

                Supported alert_kwargs:
                Slack:
                    - channel: str (channel to send slack message)
                OpsGenie:
                    - team: str (team to send opsgenie message)
                    - priority: str (priority for opsgenie alerts)

        """

    @property
    def dispatch_type(self) -> str:
        """Return the alert dispatch type"""

    @dispatch_type.setter
    def dispatch_type(self, alert_dispatch_type: str) -> None:
        """Set the alert dispatch type"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def dispatch_kwargs(self) -> Dict[str, Any]:
        """Return the dispatch kwargs"""

    @dispatch_kwargs.setter
    def dispatch_kwargs(self, dispatch_kwargs: Dict[str, Any]) -> None:
        """Set the dispatch kwargs"""

    @property
    def alert_conditions(self) -> dict[str, CustomMetricAlertCondition]:
        """Return the alert_condition that were set during metric definition"""

    @alert_conditions.setter
    def alert_conditions(
        self, alert_conditions: dict[str, CustomMetricAlertCondition]
    ) -> None:
        """Update the alert_condition that were set during metric definition"""

class CustomMetricDriftConfig:
    def __init__(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ):
        """Initialize drift config
        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            alert_config:
                Custom metric alert configuration
        """

    @property
    def repository(self) -> str:
        """Model repository"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set model repository"""

    @property
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

    @property
    def alert_config(self) -> CustomMetricAlertConfig:
        """get alert_config"""

    @alert_config.setter
    def alert_config(self, alert_config: CustomMetricAlertConfig) -> None:
        """Set alert_config"""

    @staticmethod
    def load_from_json_file(path: Path) -> "CustomMetricDriftConfig":
        """Load config from json file
        Args:
            path:
                Path to json file to load config from.
        """

    def __str__(self) -> str:
        """Return the string representation of the config."""

    def model_dump_json(self) -> str:
        """Return the json representation of the config."""

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args
        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            alert_config:
                Custom metric alert configuration
        """

class CustomMetric:
    def __init__(
        self,
        name: str,
        value: float,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float],
    ):
        """
        Initialize a custom metric for alerting.

        This class represents a custom metric that uses comparison-based alerting. It applies
        an alert condition to a single metric value.

        Args:
            name (str): The name of the metric being monitored. This should be a
                descriptive identifier for the metric.
            value (float): The current value of the metric.
             alert_threshold (AlertThreshold): The condition used to determine when an alert
                should be triggered.
             alert_threshold_value (Optional[float]): The threshold value used in conjunction with
                the  alert_threshold. If None, some alert conditions may not be applicable.

        """

    @property
    def name(self) -> str:
        """Return the metric name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the metric name"""

    @property
    def value(self) -> float:
        """Return the metric value"""

    @value.setter
    def value(self, value: float) -> None:
        """Set the metric value"""

    @property
    def alert_condition(self) -> CustomMetricAlertCondition:
        """Return the alert_condition"""

    @alert_condition.setter
    def alert_condition(self, alert_condition: CustomMetricAlertCondition) -> None:
        """Set the alert_condition"""

    @property
    def alert_threshold(self) -> AlertThreshold:
        """Return the alert_threshold"""

    @property
    def alert_threshold_value(self) -> Optional[float]:
        """Return the alert_threshold_value"""

    def __str__(self) -> str:
        """Return the string representation of the config."""

class CustomDriftProfile:
    def __init__(
        self,
        config: CustomMetricDriftConfig,
        metrics: list[CustomMetric],
        scouter_version: Optional[str] = None,
    ):
        """Initialize a CustomDriftProfile instance.

        Args:
            config (CustomMetricDriftConfig):
                The configuration for custom metric drift detection.
            metrics (list[CustomMetric]):
                A list of CustomMetric objects representing the metrics to be monitored.
            scouter_version (Optional[str]):
                The version of Scouter used to create this DriftProfile.

        Example:
            config = CustomMetricDriftConfig(...)
            metrics = [CustomMetric("accuracy", 0.95), CustomMetric("f1_score", 0.88)]
            profile = CustomDriftProfile(config, metrics, "1.0.0")
        """

    @property
    def config(self) -> CustomMetricDriftConfig:
        """Return the drift config"""

    @property
    def metrics(self) -> dict[str, float]:
        """Return custom metrics and their corresponding values"""

    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def custom_metrics(self) -> list[CustomMetric]:
        """Return custom metric objects that were used to create the drift profile"""

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> None:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to "drift_profile.json.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "CustomDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def model_validate(data: Dict[str, Any]) -> "CustomDriftProfile":
        """Load drift profile from dictionary

        Args:
            data:
                DriftProfile dictionary
        """

    def update_config_args(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            repository (Optional[str]):
                Model repository
            name (Optional[str]):
                Model name
            version (Optional[str]):
                Model version
            alert_config (Optional[CustomMetricAlertConfig]):
                Custom metric alert configuration

        Returns:
            None
        """
    # @property # hide this for now until we need it
    # def custom_metrics(self) -> list[CustomMetric]:
    #    """Return custom metric objects that were used to create the drift profile"""

class CustomDrifter:
    def __init__(self) -> None:
        """Instantiate Rust CustomMonitor class that is
        used to create monitoring profiles and compute drifts.
        """

    def create_drift_profile(
        self,
        config: CustomMetricDriftConfig,
        metrics: list[CustomMetric],
        scouter_version: Optional[str] = None,
    ) -> CustomDriftProfile:
        """Create a monitoring profile.

        Args:
            config:
                Custom metric drift config.
            metrics:
                List of custom metrics.
            scouter_version:
                Scouter version used to create DriftProfile


        Returns:
            Monitoring profile.
        """

class CustomMetricServerRecord:
    def __init__(
        self,
        repository: str,
        name: str,
        version: str,
        metric: str,
        value: int,
    ):
        """Initialize spc drift server record

        Args:
            repository:
                Model repository
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
    def repository(self) -> str:
        """Return the repository."""

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

class DataType:
    Pandas: "DataType"
    Polars: "DataType"
    Numpy: "DataType"
    Arrow: "DataType"

class DataProfiler:
    def __init__(self):
        """Instantiate Rust TestProfiler class that is
        used to profile data"""

    def create_data_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
        bin_size: int = 20,
        compute_correlations: bool = False,
    ) -> None:
        """Create a data profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or pandas dataframe. Data is expected to not contain
                any missing values, NaNs or infinities. These values must be removed or imputed.
                If NaNs or infinities are present, the data profile will not be created.
            data_type:
                Optional data type. Inferred from data if not provided.
            bin_size:
                Optional bin size for histograms. Defaults to 20 bins.
            compute_correlations:
                Whether to compute correlations or not.

        Returns:
            DataProfile
        """

# Errors
class ScouterError(Exception):
    def __init__(self, message: str) -> None: ...
    def __str__(self) -> str: ...
