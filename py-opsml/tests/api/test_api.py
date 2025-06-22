import time

from fastapi.testclient import TestClient
from scouter.client import DriftRequest, ScouterClient, TimeInterval
from scouter.types import DriftType

from tests.integration.api.conftest import PredictRequest

from .conftest import create_and_register_drift_profile, create_app


def test_api_kafka(create_artifacts):
    # create the client
    scouter_client = ScouterClient()

    # create the drift profile
    profile = create_and_register_drift_profile(client=scouter_client)
    drift_path = profile.save_to_json()

    # Create FastAPI app
    app = create_app(drift_path)

    # Configure the TestClient
    with TestClient(app) as client:
        # Simulate requests
        for _ in range(60):
            response = client.post(
                "/predict",
                json=PredictRequest(
                    feature_0=1.0,
                    feature_1=1.0,
                    feature_2=1.0,
                    feature_3=1.0,
                ).model_dump(),
            )
        assert response.status_code == 200

    time.sleep(10)

    request = DriftRequest(
        name=profile.config.name,
        space=profile.config.space,
        version=profile.config.version,
        time_interval=TimeInterval.FiveMinutes,
        max_data_points=100,
        drift_type=DriftType.Spc,
    )

    drift = scouter_client.get_binned_drift(request)

    assert drift.features.keys() == {
        "feature_0",
        "feature_1",
        "feature_2",
        "feature_3",
    }
    assert len(drift.features["feature_0"].values) == 1

    # delete the drift_path
    drift_path.unlink()
