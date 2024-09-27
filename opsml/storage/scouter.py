import json
from typing import Any, Dict, Optional, cast, List, Union

from opsml.settings.config import config
from opsml.storage.api import ApiClient, RequestType


class ScouterRoutes:
    DRIFT = "drift"
    FEATURE_DISTRIBUTION = "feature/distribution"
    HEALTHCHECK = "healthcheck"
    PROFILE = "profile"
    ALERTS = "alerts"
    ALERT_METRICS = "alerts/metrics"


class ScouterClient(ApiClient):
    def healthcheck(self) -> bool:
        """Checks if scouter server is up

        Returns:
            True if server is up, False otherwise
        """
        response = self.request(route=ScouterRoutes.HEALTHCHECK, request_type=RequestType.GET)

        return cast(str, response["message"].lower()) == "alive"

    def insert_drift_profile(self, drift_profile: str) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
        """
        profile = json.loads(drift_profile)
        self.request(route=ScouterRoutes.PROFILE, request_type=RequestType.POST, json=profile)

    def get_drift_profile(self, repository: str, name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get drift profile from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version

        Returns:
            Drift profile
        """
        response = self.request(
            route=ScouterRoutes.PROFILE,
            request_type=RequestType.GET,
            params={
                "repository": repository,
                "name": name,
                "version": version,
            },
        )

        if response["status"] == "error":
            return None

        return cast(Dict[str, Any], response["profile"])

    def update_drift_profile(self, drift_profile: str) -> Dict[str, str]:
        """Updates drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
        """
        profile = json.loads(drift_profile)
        return self.request(route=ScouterRoutes.PROFILE, request_type=RequestType.PUT, json=profile)

    def get_drift_values(
        self,
        repository: str,
        name: str,
        version: str,
        time_window: str,
        max_data_points: int,
        feature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get drift values from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            time_window:
                Time window
            max_data_points:
                Maximum data points
            feature:
                Feature to get drift values for

        Returns:
            Drift values
        """
        params = {
            "repository": repository,
            "name": name,
            "version": version,
            "time_window": time_window,
            "max_data_points": max_data_points,
        }

        if feature:
            params["feature"] = feature

        response = self.request(route=ScouterRoutes.DRIFT, request_type=RequestType.GET, params=params)

        return cast(Dict[str, Any], response["data"])

    def get_feature_distribution(
        self,
        repository: str,
        name: str,
        version: str,
        time_window: str,
        max_data_points: int,
        feature: str,
    ) -> Dict[str, Any]:
        """Get feature distribution from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            time_window:
                Time window
            max_data_points:
                Maximum data points
            feature:
                Feature to get drift values for

        Returns:
            Drift values
        """
        params = {
            "repository": repository,
            "name": name,
            "version": version,
            "time_window": time_window,
            "max_data_points": max_data_points,
            "feature": feature,
        }

        try:
            response = self.request(
                route=ScouterRoutes.FEATURE_DISTRIBUTION,
                request_type=RequestType.GET,
                params=params,
            )

            return cast(Dict[str, Any], response["data"])

        except Exception:
            return {}

    def get_monitoring_alerts(self, repository: str, name: str, version: str, active: bool, limit: int) -> List[Dict[str, Any]]:
        """Get monitoring alerts from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version

        Returns:
            Monitoring alerts
        """

        params = {
            "repository": repository,
            "name": name,
            "version": version,
            "active": active,
            "limit": limit,
        }

        try:
            response = self.request(
                route=ScouterRoutes.ALERTS,
                request_type=RequestType.GET,
                params=params,
            )

            return cast(List[Dict[str, Any]], response["data"])

        except Exception:
            return []

    def update_monitoring_alerts(self, id: int, status: str) -> Dict[str, str]:
        """Get monitoring alerts from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version

        Returns:
            Monitoring alerts
        """

        data = {"id": id, "status": status}

        try:
            response = self.request(
                route=ScouterRoutes.ALERTS,
                request_type=RequestType.PUT,
                json=data,
            )

            return cast(Dict[str, str], response)

        except Exception:
            return {"message": "Failed to update monitoring alert", "status": "error"}

    def get_alert_metrics(
        self,
        repository: str,
        name: str,
        version: str,
        time_window: str,
        max_data_points: int,
    ) -> Dict[str, Union[List[str], List[int]]]:
        """Get monitoring alerts from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            time_window:
                Time window
            max_data_points:
                Maximum data points

        Returns:
            Alert metrics is a given time period
        """

        params = {
            "repository": repository,
            "name": name,
            "version": version,
            "time_window": time_window,
            "max_data_points": max_data_points,
        }

        try:
            response = self.request(
                route=ScouterRoutes.ALERT_METRICS,
                request_type=RequestType.GET,
                params=params,
            )

            return cast(Dict[str, Union[List[str], List[int]]], response["data"])

        except Exception:
            return {
                "created_at": [],
                "alert_count": [],
                "active": [],
                "acknowledged": [],
            }


SCOUTER_CLIENT = None
if config.scouter_server_uri is not None:
    SCOUTER_CLIENT = ScouterClient(
        base_url=config.scouter_server_uri,
        username=config.scouter_username,
        password=config.scouter_password,
        use_auth=config.scouter_auth,
        token=None,
        path_prefix=config.scouter_path_prefix,
    )
