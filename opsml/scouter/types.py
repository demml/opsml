from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ScouterHealthCheckResponse(BaseModel):
    running: bool


class DriftProfileRequest(BaseModel):
    drift_type: str
    profile: str


class DriftProfileUpdateRequest(BaseModel):
    repository: str
    name: str
    version: str
    profile: str
    save: bool = False
    drift_type: str


class GetDriftProfileResponse(BaseModel):
    profile: Optional[Dict[str, Any]]


class DriftFeature(BaseModel):
    created_at: List[str]
    values: List[float]


class DriftResponse(BaseModel):
    features: Dict[str, DriftFeature]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class FeatureDistribution(BaseModel):
    name: str
    repository: str
    version: str
    percentile_10: float = 0.0
    percentile_20: float = 0.0
    percentile_30: float = 0.0
    percentile_40: float = 0.0
    percentile_50: float = 0.0
    percentile_60: float = 0.0
    percentile_70: float = 0.0
    percentile_80: float = 0.0
    percentile_90: float = 0.0
    percentile_100: float = 0.0
    val_10: float = 0.0
    val_20: float = 0.0
    val_30: float = 0.0
    val_40: float = 0.0
    val_50: float = 0.0
    val_60: float = 0.0
    val_70: float = 0.0
    val_80: float = 0.0
    val_90: float = 0.0
    val_100: float = 0.0


class MonitorAlert(BaseModel):
    created_at: str
    name: str
    repository: str
    version: str
    feature: str
    alerts: Dict[str, str]
    status: str
    id: int


class MonitorAlerts(BaseModel):
    alerts: List[MonitorAlert]


class UpdateAlertRequest(BaseModel):
    id: int
    status: str


class UpdateAlert(BaseModel):
    status: str
    message: str


class AlertMetrics(BaseModel):
    created_at: List[str]
    alert_count: List[int]
    active: List[int]
    acknowledged: List[int]


class UpdateProfileStatus(BaseModel):
    name: str
    repository: str
    version: str
    status: bool
