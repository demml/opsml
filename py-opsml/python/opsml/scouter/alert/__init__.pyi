# pylint: disable=dangerous-default-value

from typing import Dict, List, Optional

from ..types import CommonCrons

class ConsoleDispatchConfig:
    def __init__(self):
        """Initialize alert config"""

    @property
    def enabled(self) -> bool:
        """Return the alert dispatch type"""

class SlackDispatchConfig:
    def __init__(self, channel: str):
        """Initialize alert config

        Args:
            channel:
                Slack channel name for where alerts will be reported
        """

    @property
    def channel(self) -> str:
        """Return the slack channel name"""

    @channel.setter
    def channel(self, channel: str) -> None:
        """Set the slack channel name for where alerts will be reported"""

class OpsGenieDispatchConfig:
    def __init__(self, team: str):
        """Initialize alert config

        Args:
            team:
                Opsegenie team to be notified in the event of drift
        """

    @property
    def team(self) -> str:
        """Return the opesgenie team name"""

    @team.setter
    def team(self, team: str) -> None:
        """Set the opesgenie team name"""

class AlertDispatchType:
    Slack: "AlertDispatchType"
    OpsGenie: "AlertDispatchType"
    Console: "AlertDispatchType"

    @staticmethod
    def to_string() -> str:
        """Return the string representation of the alert dispatch type"""

DispatchConfigType = ConsoleDispatchConfig | SlackDispatchConfig | OpsGenieDispatchConfig

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
        rule: str = "8 16 4 8 2 4 1 1",
        zones_to_monitor: List[AlertZone] = [
            AlertZone.Zone1,
            AlertZone.Zone2,
            AlertZone.Zone3,
            AlertZone.Zone4,
        ],
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

class PsiNormalThreshold:
    def __init__(self, alpha: float = 0.05):
        """Initialize PSI threshold using normal approximation.

        Uses the asymptotic normal distribution of PSI to calculate critical values
        for population drift detection.

        Args:
            alpha: Significance level (0.0 to 1.0, exclusive). Common values:
                   0.05 (95% confidence), 0.01 (99% confidence)

        Raises:
            ValueError: If alpha not in range (0.0, 1.0)
        """

    @property
    def alpha(self) -> float:
        """Statistical significance level for drift detection."""

    @alpha.setter
    def alpha(self, alpha: float) -> None:
        """Set significance level (must be between 0.0 and 1.0, exclusive)."""

class PsiChiSquareThreshold:
    def __init__(self, alpha: float = 0.05):
        """Initialize PSI threshold using chi-square approximation.

        Uses the asymptotic chi-square distribution of PSI.

        The chi-square method is generally more statistically rigorous than
        normal approximation, especially for smaller sample sizes.

        Args:
            alpha: Significance level (0.0 to 1.0, exclusive). Common values:
                   0.05 (95% confidence), 0.01 (99% confidence)

        Raises:
            ValueError: If alpha not in range (0.0, 1.0)
        """

    @property
    def alpha(self) -> float:
        """Statistical significance level for drift detection."""

    @alpha.setter
    def alpha(self, alpha: float) -> None:
        """Set significance level (must be between 0.0 and 1.0, exclusive)."""

class PsiFixedThreshold:
    def __init__(self, threshold: float = 0.25):
        """Initialize PSI threshold using a fixed value.

        Uses a predetermined PSI threshold value, similar to traditional
        "rule of thumb" approaches (e.g., 0.10 for moderate drift, 0.25
        for significant drift).

        Args:
            threshold: Fixed PSI threshold value (must be positive).
                      Common industry values: 0.10, 0.25

        Raises:
            ValueError: If threshold is not positive
        """

    @property
    def threshold(self) -> float:
        """Fixed PSI threshold value for drift detection."""

    @threshold.setter
    def threshold(self, threshold: float) -> None:
        """Set threshold value (must be positive)."""

PsiThresholdType = PsiNormalThreshold | PsiChiSquareThreshold | PsiFixedThreshold

class PsiAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        features_to_monitor: List[str] = [],
        threshold: Optional[PsiThresholdType] = PsiChiSquareThreshold(),
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch configuration to use. Defaults to an internal "Console" type where
                the alerts will be logged to the console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features
            threshold:
                Configuration that helps determine how to calculate PSI critical values.
                Defaults to PsiChiSquareThreshold, which uses the chi-square distribution.
        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def threshold(self) -> PsiThresholdType:
        """Return the threshold config"""

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

class SpcAlertConfig:
    def __init__(
        self,
        rule: SpcAlertRule = SpcAlertRule(),
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        features_to_monitor: List[str] = [],
    ):
        """Initialize alert config

        Args:
            rule:
                Alert rule to use. Defaults to Standard
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight
            features_to_monitor:
                List of features to monitor. Defaults to empty list, which means all features

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

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

class AlertThreshold:
    """
    Enum representing different alert conditions for monitoring metrics.

    Attributes:
        Below: Indicates that an alert should be triggered when the metric is below a threshold.
        Above: Indicates that an alert should be triggered when the metric is above a threshold.
        Outside: Indicates that an alert should be triggered when the metric is outside a specified range.
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
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def alert_conditions(self) -> dict[str, CustomMetricAlertCondition]:
        """Return the alert_condition that were set during metric definition"""

    @alert_conditions.setter
    def alert_conditions(self, alert_conditions: dict[str, CustomMetricAlertCondition]) -> None:
        """Update the alert_condition that were set during metric definition"""

class LLMAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
    ):
        """Initialize alert config

        Args:
            dispatch_config:
                Alert dispatch config. Defaults to console
            schedule:
                Schedule to run monitor. Defaults to daily at midnight

        """

    @property
    def dispatch_type(self) -> AlertDispatchType:
        """Return the alert dispatch type"""

    @property
    def dispatch_config(self) -> DispatchConfigType:
        """Return the dispatch config"""

    @property
    def schedule(self) -> str:
        """Return the schedule"""

    @schedule.setter
    def schedule(self, schedule: str) -> None:
        """Set the schedule"""

    @property
    def alert_conditions(self) -> Optional[Dict[str, LLMMetricAlertCondition]]:
        """Return the alert conditions"""

class LLMMetricAlertCondition:
    def __init__(
        self,
        alert_threshold: AlertThreshold,
        alert_threshold_value: Optional[float],
    ):
        """Initialize a LLMMetricAlertCondition instance.
        Args:
            alert_threshold (AlertThreshold):
                The condition that determines when an alert should be triggered.
                Must be one of the AlertThreshold enum members like Below, Above, or Outside.
            alert_threshold_value (Optional[float], optional):
                A numerical boundary used in conjunction with the alert_threshold.
                This can be None for certain types of comparisons that don't require a fixed boundary.
        Example:
            alert_threshold = LLMMetricAlertCondition(AlertCondition.BELOW, 2.0)
        """

    def __str__(self) -> str:
        """Return the string representation of LLMMetricAlertCondition."""
