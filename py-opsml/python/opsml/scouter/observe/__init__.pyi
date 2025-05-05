from typing import Dict, List, Optional

from ..queue import ServerRecords

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
        """Return the metrics"""

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
    def space(self) -> str:
        """Return the space"""

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
    def __init__(self, space: str, name: str, version: str) -> None:
        """Initializes an api metric observer

        Args:
            space:
                Model space
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
