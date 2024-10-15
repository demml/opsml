"""This is the Scouter Server Integration that is used when opsml is running in server mode.
Scouter is a separate server that is used to store drift profiles and monitor model drift.
"""

import json
from typing import Any, Dict, List, Optional, Union, cast

from opsml.helpers.logging import ArtifactLogger
from opsml.scouter import DriftType
from opsml.settings.config import config
from opsml.storage.api import ApiClient, RequestType

logger = ArtifactLogger.get_logger()


class ScouterRoutes:
    DRIFT = "drift"
    FEATURE_DISTRIBUTION = "feature/distribution"
    HEALTHCHECK = "healthcheck"
    PROFILE = "profile"
    PROFILE_STATUS = "profile/status"
    ALERTS = "alerts"
    ALERT_METRICS = "alerts/metrics"
    OBSERVABILITY_METRICS = "observability/metrics"


class ScouterServerClient(ApiClient):
    def healthcheck(self) -> bool:
        """Checks if scouter server is up

        Returns:
            True if server is up, False otherwise
        """
        response = self.request(route=ScouterRoutes.HEALTHCHECK, request_type=RequestType.GET)

        return cast(str, response["message"].lower()) == "alive"

    def insert_drift_profile(self, drift_profile: str, drift_type: DriftType) -> None:
        """Inserts drift profile into scouter server

        Args:
            drift_profile:
                Drift profile to insert
            drift_type:
                Drift type
        """
        data = {"profile": json.loads(drift_profile), "drift_type": drift_type.value}
        self.request(route=ScouterRoutes.PROFILE, request_type=RequestType.POST, json=data)

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

        return cast(Dict[str, Any], response["data"])

    def update_drift_profile(
        self, repository: str, name: str, version: str, drift_profile: str, drift_type: DriftType, save: bool = False
    ) -> Dict[str, str]:
        """Updates drift profile into scouter server

        Args:
            name:
                Model name
            repository:
                Model repository
            version:
                Model version
            drift_profile:
                Drift profile to insert
            drift_type:
                Drift type
            save:
                Save flag
        """
        logger.info("Updating scouter server drift profile for {}/{}/{}", repository, name, version)

        data = {"profile": json.loads(drift_profile), "drift_type": drift_type.value}
        return self.request(route=ScouterRoutes.PROFILE, request_type=RequestType.PUT, json=data)

    def update_drift_profile_status(self, repository: str, name: str, version: str, active: bool) -> Dict[str, str]:
        """Updates drift profile status into scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            status:
                Status to update
        """
        return self.request(
            route=ScouterRoutes.PROFILE_STATUS,
            request_type=RequestType.PUT,
            json={
                "repository": repository,
                "name": name,
                "version": version,
                "active": active,
            },
        )

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

        except Exception:  # pylint: disable=broad-except
            return {}

    def get_monitoring_alerts(
        self, repository: str, name: str, version: str, active: bool, limit: int
    ) -> List[Dict[str, Any]]:
        """Get monitoring alerts from scouter server

        Args:
            repository:
                Model repository
            name:
                Model name
            version:
                Model version
            active:
                Active alerts
            limit:
                Maximum number of alerts to return

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

        except Exception:  # pylint: disable=broad-except
            return []

    def update_monitoring_alerts(self, id_num: int, status: str) -> Dict[str, str]:
        """Get monitoring alerts from scouter server

        Args:
            id_num:
                Monitoring alert id
            status:
                Status of monitoring alert

        Returns:
            Monitoring alerts
        """

        try:
            response = self.request(
                route=ScouterRoutes.ALERTS,
                request_type=RequestType.PUT,
                json={"id": id_num, "status": status},
            )

            return cast(Dict[str, str], response)

        except Exception:  # pylint: disable=broad-except
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

        except Exception:  # pylint: disable=broad-except
            return {
                "created_at": [],
                "alert_count": [],
                "active": [],
                "acknowledged": [],
            }

    def get_observability_metrics(
        self,
        repository: str,
        name: str,
        version: str,
        time_window: str,
        max_data_points: int,
    ) -> List[Dict[str, Any]]:
        """Get monitoring observability metrics from scouter server

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
                route=ScouterRoutes.OBSERVABILITY_METRICS,
                request_type=RequestType.GET,
                params=params,
            )

            return cast(List[Dict[str, Any]], response["data"])

        except Exception:  # pylint: disable=broad-except
            return []


SCOUTER_SERVER_CLIENT = None
if config.scouter_server_uri is not None:
    logger.info("Initializing Scouter Server Client")
    SCOUTER_SERVER_CLIENT = ScouterServerClient(
        base_url=config.scouter_server_uri,
        username=config.scouter_username,
        password=config.scouter_password,
        use_auth=config.scouter_auth,
        token=None,
        path_prefix=config.scouter_path_prefix,
    )
    logger.info("Scouter Server Client Initialized")
