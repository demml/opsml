# type: ignore
# pylint: disable=no-name-in-module
from .. import scouter

OpsGenieDispatchConfig = scouter.alertOpsGenieDispatchConfig
ConsoleDispatchConfig = scouter.alertConsoleDispatchConfig
AlertDispatchType = scouter.alertAlertDispatchType
AlertThreshold = scouter.alertAlertThreshold
AlertZone = scouter.alertAlertZone
CustomMetricAlertCondition = scouter.alertCustomMetricAlertCondition
CustomMetricAlertConfig = scouter.alertCustomMetricAlertConfig
PsiAlertConfig = scouter.alertPsiAlertConfig
SpcAlert = scouter.alertSpcAlert
SpcAlertConfig = scouter.alertSpcAlertConfig
SpcAlertRule = scouter.alertSpcAlertRule
SpcAlertType = scouter.alertSpcAlertType
SlackDispatchConfig = scouter.alertSlackDispatchConfig


__all__ = [
    "AlertZone",
    "SpcAlertType",
    "SpcAlertRule",
    "PsiAlertConfig",
    "SpcAlertConfig",
    "SpcAlert",
    "AlertThreshold",
    "CustomMetricAlertCondition",
    "CustomMetricAlertConfig",
    "SlackDispatchConfig",
    "OpsGenieDispatchConfig",
    "ConsoleDispatchConfig",
    "AlertDispatchType",
]
