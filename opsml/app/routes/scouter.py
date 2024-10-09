# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access


from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from scouter import DriftType, SpcDriftProfile

from opsml.app.routes.pydantic_models import Success
from opsml.helpers.logging import ArtifactLogger
from opsml.scouter.server import ScouterServerClient
from opsml.scouter.types import (
    AlertMetrics,
    DriftProfileRequest,
    DriftProfileUpdateRequest,
    DriftResponse,
    FeatureDistribution,
    GetDriftProfileResponse,
    MonitorAlerts,
    ProfileUpdateResponse,
    ScouterHealthCheckResponse,
    UpdateAlert,
    UpdateAlertRequest,
    UpdateProfileStatus,
)
from opsml.storage.client import StorageClientBase
from opsml.types import RegistryTableNames, SaveName, Suffix

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.get("/scouter/healthcheck", name="scouter server status", response_model=ScouterHealthCheckResponse)
def check_server(
    request: Request,
) -> ScouterHealthCheckResponse:
    """Checks if scouter-server is running

    Args:
        request:
            FastAPI request object

    Returns:
        bool
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        return ScouterHealthCheckResponse(
            running=client.healthcheck(),
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error(f"Scouter server healthcheck failed: {error}")
        return ScouterHealthCheckResponse(
            running=False,
        )


@router.post("/scouter/drift/profile", name="insert_drift_profile", response_model=Success)
def insert_profile(request: Request, payload: DriftProfileRequest) -> Success:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        payload:
            DriftProfileRequest

    Returns:
        200
    """

    try:
        drift_type = DriftType.from_value(payload.drift_type)
        client: ScouterServerClient = request.app.state.scouter_client
        client.insert_drift_profile(
            drift_profile=payload.profile,
            drift_type=drift_type,
        )
        return Success()
    except Exception as error:
        logger.error(f"Failed to insert drift profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert drift profile"
        ) from error


@router.put("/scouter/drift/profile", name="update_drift_profile", response_model=ProfileUpdateResponse)
def update_profile(request: Request, payload: DriftProfileUpdateRequest) -> ProfileUpdateResponse:
    """Updates a drift profile to scouter-server as well as modelcard storage

    Args:
        request:
            FastAPI request object
        payload:
            DriftProfileRequest

    Returns:
        200
    """

    client: ScouterServerClient = request.app.state.scouter_client
    storage_root: str = request.app.state.storage_root
    storage_client: StorageClientBase = request.app.state.storage_client
    drift_type = DriftType.from_value(payload.drift_type)
    try:
        if drift_type == DriftType.SPC:
            profile = SpcDriftProfile.model_validate_json(payload.profile)

        # need to validate the profile before updating
        response = client.update_drift_profile(
            repository=payload.repository,
            name=payload.name,
            version=payload.version,
            drift_profile=payload.profile,
            drift_type=DriftType.from_str(payload.drift_type),
            save=payload.save,
        )

        if response["status"] == "error":
            return ProfileUpdateResponse(
                complete=False,
                message=response["message"],
            )

        # this route is only used for updating the drift profile from the UI
        # Updating cards and profiles should be done via update_card
        if payload.save:
            save_path = Path(
                storage_root,
                RegistryTableNames.MODEL.value,
                payload.repository,
                payload.name,
                f"v{payload.version}",
                SaveName.DRIFT_PROFILE.value,
            ).with_suffix(Suffix.JSON.value)

            with TemporaryDirectory() as tempdir:
                temp_path = (Path(tempdir) / SaveName.DRIFT_PROFILE.value).with_suffix(Suffix.JSON.value)
                profile.save_to_json(temp_path)
                storage_client.put(temp_path, save_path)

        return ProfileUpdateResponse()
    except Exception as error:
        logger.error(f"Failed to insert drift profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert drift profile"
        ) from error


@router.get("/scouter/drift/profile", name="get_profile", response_model=GetDriftProfileResponse)
def get_profile(
    request: Request,
    repository: str,
    name: str,
    version: str,
) -> GetDriftProfileResponse:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
        repository:
            Model repository
        name:
            Model name
        version:
            Model version

    Returns:
        DriftProfile string
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        profile = client.get_drift_profile(repository, name, version)
        return GetDriftProfileResponse(profile=profile)
    except Exception as error:
        logger.error(f"Failed to get drift profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get drift profile"
        ) from error


@router.get("/scouter/drift/values", name="get_drift", response_model=DriftResponse)
def get_drift_values(
    request: Request,
    repository: str,
    name: str,
    version: str,
    time_window: str,
    max_data_points: int,
    feature: Optional[str] = None,
) -> DriftResponse:
    """Uploads drift profile to scouter-server

    Args:
        request:
            FastAPI request object
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
        DriftProfile string
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.get_drift_values(
            repository,
            name,
            version,
            time_window,
            max_data_points,
            feature,
        )

        return DriftResponse(**values)
    except Exception as error:
        logger.error(f"Failed to get drift values: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get drift values"
        ) from error


@router.get("/scouter/feature/distribution", name="feature distribution", response_model=FeatureDistribution)
def get_feature_distribution(
    request: Request,
    repository: str,
    name: str,
    version: str,
    time_window: str,
    max_data_points: int,
    feature: str,
) -> FeatureDistribution:
    """Gets feature distribution from scouter-server. This is a UI only route

    Args:
        request:
            FastAPI request object
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
        FeatureDistribution
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.get_feature_distribution(
            repository,
            name,
            version,
            time_window,
            max_data_points,
            feature,
        )

        if not values:
            values["name"] = name
            values["repository"] = repository
            values["version"] = version

        return FeatureDistribution(**values)
    except Exception as error:
        logger.error(f"Failed to calculate feature distribution: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate feature distribution",
        ) from error


@router.get("/scouter/alerts", name="monitoring alerts", response_model=MonitorAlerts)
def get_monitoring_alerts(
    request: Request,
    repository: str,
    name: str,
    version: str,
    active: bool,
    limit: int,
) -> MonitorAlerts:
    """Gets monitoring alerts from the scouter-server. This is a UI only route

    Args:
        request:
            FastAPI request object
        repository:
            Model repository
        name:
            Model name
        version:
            Model version
        active:
            Active alerts
        limit:
            Limit of alerts to retrieve

    Returns:
        DriftProfile string
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.get_monitoring_alerts(repository, name, version, active, limit)

        return MonitorAlerts(alerts=values)
    except Exception as error:
        logger.error(f"Failed to retrieve alerts: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts",
        ) from error


@router.put("/scouter/alerts", name="monitoring alerts", response_model=UpdateAlert)
def update_monitoring_alerts(
    request: Request,
    payload: UpdateAlertRequest,
) -> UpdateAlert:
    """Gets monitoring alerts from the scouter-server. This is a UI only route

    Args:
        request:
            FastAPI request object
        payload:
            UpdateAlertRequest

    Returns:
        UpdateAlert
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.update_monitoring_alerts(
            id_num=payload.id,
            status=payload.status,
        )

        return UpdateAlert(**values)
    except Exception as error:
        logger.error(f"Failed to update alert: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert",
        ) from error


@router.get("/scouter/alerts/metrics", name="monitoring alert metrics", response_model=AlertMetrics)
def get_alert_metrics(
    request: Request,
    repository: str,
    name: str,
    version: str,
    time_window: str,
    max_data_points: int,
) -> AlertMetrics:
    """Gets monitoring alerts from the scouter-server. This is a UI only route

    Args:
        request:
            FastAPI request object
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
        AlertMetrics
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.get_alert_metrics(repository, name, version, time_window, max_data_points)

        return AlertMetrics(**values)
    except Exception as error:
        logger.error(f"Failed to retrieve alert metrics: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert metrics",
        ) from error


@router.put("/scouter/profile/status", name="profile status", response_model=UpdateAlert)
def update_profile_status(
    request: Request,
    payload: UpdateProfileStatus,
) -> UpdateAlert:
    """Updates the status of a profile

    Args:
        request:
            FastAPI request object
        payload:
            UpdateAlertRequest

    Returns:
        UpdateAlert
    """

    client: ScouterServerClient = request.app.state.scouter_client

    try:
        values = client.update_drift_profile_status(
            repository=payload.repository,
            name=payload.name,
            version=payload.version,
            status=payload.st,
        )

        return UpdateAlert(**values)
    except Exception as error:
        logger.error(f"Failed to update alert: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert",
        ) from error
