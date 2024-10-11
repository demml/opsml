from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ProfileUpdateResponse(BaseModel):
    complete: bool = True
    message: str = "Profile updated successfully"


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
    alert: Dict[str, str]
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


class ObservabilityMetric(BaseModel):
    route_name: str
    created_at: List[str]
    total_request_per_sec: float
    total_error_per_sec: float
    total_request_count: int
    total_error_count: int
    p5: List[float]
    p25: List[float]
    p50: List[float]
    p95: List[float]
    p99: List[float]
    request_per_sec: List[float]
    error_per_sec: List[float]
    error_latency: List[float]
    status_counts: List[Dict[str, int]]


class ObservabilityMetrics(BaseModel):
    metrics: List[Optional[ObservabilityMetric]]


class UpdateProfileStatus(BaseModel):
    name: str
    repository: str
    version: str
    active: bool
