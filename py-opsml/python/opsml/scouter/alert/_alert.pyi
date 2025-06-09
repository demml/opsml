# pylint: disable=dangerous-default-value

from typing import List, Optional

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

class PsiAlertConfig:
    def __init__(
        self,
        dispatch_config: Optional[SlackDispatchConfig | OpsGenieDispatchConfig] = None,
        schedule: Optional[str | CommonCrons] = None,
        features_to_monitor: List[str] = [],
        psi_threshold: float = 0.25,
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
            psi_threshold:
                What threshold must be met before sending alert messages default is 0.25

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
    def features_to_monitor(self) -> List[str]:
        """Return the features to monitor"""

    @features_to_monitor.setter
    def features_to_monitor(self, features_to_monitor: List[str]) -> None:
        """Set the features to monitor"""

    @property
    def psi_threshold(self) -> float:
        """Return the schedule"""

    @psi_threshold.setter
    def psi_threshold(self, threshold: float) -> None:
        """Set the schedule"""

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
