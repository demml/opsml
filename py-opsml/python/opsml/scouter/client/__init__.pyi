import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..types import DriftType

class HTTPConfig:
    server_uri: str
    username: str
    password: str
    auth_token: str

    def __init__(
        self,
        server_uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> None:
        """HTTP configuration to use with the HTTPProducer.

        Args:
            server_uri:
                URL of the HTTP server to publish messages to.
                If not provided, the value of the HTTP_server_uri environment variable is used.

            username:
                Username for basic authentication.

            password:
                Password for basic authentication.

            auth_token:
                Authorization token to use for authentication.

        """

class TimeInterval:
    FiveMinutes: "TimeInterval"
    FifteenMinutes: "TimeInterval"
    ThirtyMinutes: "TimeInterval"
    OneHour: "TimeInterval"
    ThreeHours: "TimeInterval"
    SixHours: "TimeInterval"
    TwelveHours: "TimeInterval"
    TwentyFourHours: "TimeInterval"
    TwoDays: "TimeInterval"
    FiveDays: "TimeInterval"

class DriftRequest:
    def __init__(
        self,
        name: str,
        space: str,
        version: str,
        time_interval: TimeInterval,
        max_data_points: int,
        drift_type: DriftType,
    ) -> None:
        """Initialize drift request

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            time_interval:
                Time window for drift request
            max_data_points:
                Maximum data points to return
            drift_type:
                Drift type for request
        """

class ProfileStatusRequest:
    def __init__(self, name: str, space: str, version: str, drift_type: DriftType, active: bool) -> None:
        """Initialize profile status request

        Args:
            name:
                Model name
            space:
                Model space
            version:
                Model version
            drift_type:
                Profile drift type. A (repo/name/version can be associated with more than one drift type)
            active:
                Whether to set the profile as active or inactive
        """

class GetProfileRequest:
    def __init__(self, name: str, space: str, version: str, drift_type: DriftType) -> None:
        """Initialize get profile request

        Args:
            name:
                Profile name
            space:
                Profile space
            version:
                Profile version
            drift_type:
                Profile drift type. A (repo/name/version can be associated with more than one drift type)
        """

class Alert:
    created_at: datetime.datetime
    name: str
    space: str
    version: str
    feature: str
    alert: str
    id: int
    status: str

class DriftAlertRequest:
    def __init__(
        self,
        name: str,
        space: str,
        version: str,
        active: bool = False,
        limit_datetime: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
    ) -> None:
        """Initialize drift alert request

        Args:
            name:
                Name
            space:
                Space
            version:
                Version
            active:
                Whether to get active alerts only
            limit_datetime:
                Limit datetime for alerts
            limit:
                Limit for number of alerts to return
        """

# Client
class ScouterClient:
    """Helper client for interacting with Scouter Server"""

    def __init__(self, config: Optional[HTTPConfig] = None) -> None:
        """Initialize ScouterClient

        Args:
            config:
                HTTP configuration for interacting with the server.
        """

    def get_binned_drift(self, drift_request: DriftRequest) -> Any:
        """Get drift map from server

        Args:
            drift_request:
                DriftRequest object

        Returns:
            Drift map of type BinnedMetrics | BinnedPsiFeatureMetrics | BinnedSpcFeatureMetrics
        """

    def register_profile(self, profile: Any, set_active: bool = False) -> bool:
        """Registers a drift profile with the server

        Args:
            profile:
                Drift profile
            set_active:
                Whether to set the profile as active or inactive

        Returns:
            boolean
        """

    def update_profile_status(self, request: ProfileStatusRequest) -> bool:
        """Update profile status

        Args:
            request:
                ProfileStatusRequest

        Returns:
            boolean
        """

    def get_alerts(self, request: DriftAlertRequest) -> List[Alert]:
        """Get alerts

        Args:
            request:
                DriftAlertRequest

        Returns:
            List[Alert]
        """

    def download_profile(self, request: GetProfileRequest, path: Optional[Path]) -> str:
        """Download profile

        Args:
            request:
                GetProfileRequest
            path:
                Path to save profile

        Returns:
            Path to downloaded profile
        """

class BinnedMetricStats:
    avg: float
    lower_bound: float
    upper_bound: float

    def __str__(self) -> str: ...

class BinnedMetric:
    metric: str
    created_at: List[datetime.datetime]
    stats: List[BinnedMetricStats]

    def __str__(self) -> str: ...

class BinnedMetrics:
    @property
    def metrics(self) -> Dict[str, BinnedMetric]: ...
    def __str__(self) -> str: ...

class BinnedPsiMetric:
    created_at: List[datetime.datetime]
    psi: List[float]
    overall_psi: float
    bins: Dict[int, float]

    def __str__(self) -> str: ...

class BinnedPsiFeatureMetrics:
    features: Dict[str, BinnedMetric]

    def __str__(self) -> str: ...

class SpcDriftFeature:
    created_at: List[datetime.datetime]
    values: List[float]

    def __str__(self) -> str: ...

class BinnedSpcFeatureMetrics:
    features: Dict[str, SpcDriftFeature]

    def __str__(self) -> str: ...
