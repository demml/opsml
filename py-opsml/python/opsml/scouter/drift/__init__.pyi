# pylint: disable=dangerous-default-value
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, overload

from ..alert import (
    AlertThreshold,
    CustomMetricAlertCondition,
    CustomMetricAlertConfig,
    PsiAlertConfig,
    SpcAlertConfig,
)
from ..types import DataType, DriftType

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

class SpcDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_size: int = 25,
        alert_config: SpcAlertConfig = SpcAlertConfig(),
        config_path: Optional[Path] = None,
    ):
        """Initialize monitor config

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            sample_size:
                Sample size
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
    def name(self) -> str:
        """Model Name"""

    @name.setter
    def name(self, name: str) -> None:
        """Set model name"""

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @property
    def alert_config(self) -> SpcAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: SpcAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

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
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample_size: Optional[int] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            sample_size:
                Sample size
            alert_config:
                Alert configuration
        """

class SpcDriftProfile:
    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, SpcFeatureDriftProfile]:
        """Return the list of features."""

    @property
    def config(self) -> SpcDriftConfig:
        """Return the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `spc_drift_profile.json`


        Returns:
            Path to the saved json file
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def from_file(path: Path) -> "SpcDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
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
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        sample_size: Optional[int] = None,
        alert_config: Optional[SpcAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            sample_size:
                Sample size
            alert_config:
                Alert configuration
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

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

    @property
    def space(self) -> str:
        """Space to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, SpcFeatureDrift]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of data drift"""

    def model_dump_json(self) -> str:
        """Return json representation of data drift"""

    @staticmethod
    def model_validate_json(json_string: str) -> "SpcDriftMap":
        """Load drift map from json file.

        Args:
            json_string:
                JSON string representation of the drift map
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to `spc_drift_map.json`

        Returns:
            Path to the saved json file

        """

    def to_numpy(self) -> Any:
        """Return drift map as a tuple of sample_array, drift_array and list of features"""

class PsiDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        alert_config: PsiAlertConfig = PsiAlertConfig(),
        config_path: Optional[Path] = None,
    ):
        """Initialize monitor config

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
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
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

    @property
    def version(self) -> str:
        """Model version"""

    @version.setter
    def version(self, version: str) -> None:
        """Set model version"""

    @property
    def feature_map(self) -> Optional[FeatureMap]:
        """Feature map"""

    @property
    def alert_config(self) -> PsiAlertConfig:
        """Alert configuration"""

    @alert_config.setter
    def alert_config(self, alert_config: PsiAlertConfig) -> None:
        """Set alert configuration"""

    @property
    def drift_type(self) -> DriftType:
        """Drift type"""

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
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[PsiAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version
            alert_config:
                Alert configuration
        """

class PsiDriftProfile:
    @property
    def scouter_version(self) -> str:
        """Return scouter version used to create DriftProfile"""

    @property
    def features(self) -> Dict[str, PsiFeatureDriftProfile]:
        """Return the list of features."""

    @property
    def config(self) -> PsiDriftConfig:
        """Return the monitor config."""

    def model_dump_json(self) -> str:
        """Return json representation of drift profile"""

    def model_dump(self) -> Dict[str, Any]:
        """Return dictionary representation of drift profile"""

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `psi_drift_profile.json`

        Returns:
            Path to the saved json file
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PsiDriftProfile":
        """Load drift profile from json

        Args:
            json_string:
                JSON string representation of the drift profile

        """

    @staticmethod
    def from_file(path: Path) -> "PsiDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
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
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[PsiAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            alert_config:
                Alert configuration
        """

    def __str__(self) -> str:
        """Sting representation of DriftProfile"""

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

class BinType:
    Binary: "BinType"
    Numeric: "BinType"
    Category: "BinType"

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

    @property
    def bin_type(self) -> BinType:
        """Return the timestamp."""

class PsiDriftMap:
    """Drift map of features"""

    @property
    def space(self) -> str:
        """Space to associate with drift map"""

    @property
    def name(self) -> str:
        """name to associate with drift map"""

    @property
    def version(self) -> str:
        """Version to associate with drift map"""

    @property
    def features(self) -> Dict[str, float]:
        """Returns dictionary of features and their reported drift, if any"""

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

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift map to json file

        Args:
            path:
                Optional path to save the drift map. If None, outputs to `psi_drift_map.json`

        Returns:
            Path to the saved json file

        """

class CustomMetricDriftConfig:
    def __init__(
        self,
        space: str = "__missing__",
        name: str = "__missing__",
        version: str = "0.1.0",
        sample_size: int = 25,
        alert_config: CustomMetricAlertConfig = CustomMetricAlertConfig(),
    ):
        """Initialize drift config
        Args:
            space:
                Model space
            name:
                Model name
            version:
                Model version. Defaults to 0.1.0
            alert_config:
                Custom metric alert configuration
        """

    @property
    def space(self) -> str:
        """Model space"""

    @space.setter
    def space(self, space: str) -> None:
        """Set model space"""

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
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args
        Args:
            space:
                Model space
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
        alert_threshold_value: Optional[float] = None,
    ):
        """
        Initialize a custom metric for alerting.

        This class represents a custom metric that uses comparison-based alerting. It applies
        an alert condition to a single metric value.

        Args:
            name (str): The name of the metric being monitored. This should be a
                descriptive identifier for the metric.
            value (float): The current value of the metric.
            alert_threshold (AlertThreshold):
                The condition used to determine when an alert should be triggered.
            alert_threshold_value (Optional[float]):
                The threshold or boundary value used in conjunction with the alert_threshold.
                If supplied, this value will be added or subtracted from the provided metric value to
                determine if an alert should be triggered.

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

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save drift profile to json file

        Args:
            path:
                Optional path to save the drift profile. If None, outputs to `custom_drift_profile.json`

        Returns:
            Path to the saved json file
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

    @staticmethod
    def from_file(path: Path) -> "CustomDriftProfile":
        """Load drift profile from file

        Args:
            path: Path to the file
        """

    def update_config_args(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        alert_config: Optional[CustomMetricAlertConfig] = None,
    ) -> None:
        """Inplace operation that updates config args

        Args:
            space (Optional[str]):
                Model space
            name (Optional[str]):
                Model name
            version (Optional[str]):
                Model version
            alert_config (Optional[CustomMetricAlertConfig]):
                Custom metric alert configuration

        Returns:
            None
        """

class Drifter:
    def __init__(self) -> None:
        """Instantiate Rust Drifter class that is
        used to create monitoring profiles and compute drifts.
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile:
        """Create a PSI (population stability index) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                PsiDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            PsiDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Union[CustomMetric, List[CustomMetric]],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile:
        """Create a custom drift profile from data.

        Args:
            data:
                CustomMetric or list of CustomMetric.
            config:
                CustomMetricDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            CustomDriftProfile
        """

    def create_drift_profile(  # type: ignore
        self,
        data: Any,
        config: Optional[Union[SpcDriftConfig, PsiDriftConfig, CustomMetricDriftConfig]] = None,
        data_type: Optional[DataType] = None,
    ) -> Union[SpcDriftProfile, PsiDriftProfile, CustomDriftProfile]:
        """Create a drift profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe, pandas dataframe or a list of CustomMetric if creating
                a custom metric profile.
            config:
                Drift config that will be used for monitoring
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def compute_drift(
        self,
        data: Any,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile],
        data_type: Optional[DataType] = None,
    ) -> Any:
        """Create a drift profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe, pandas dataframe or a list of CustomMetric if creating
                a custom metric profile.
            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftMap or PsiDriftMap
        """
