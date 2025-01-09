# type: ignore

from pathlib import Path
from tempfile import TemporaryDirectory

from opsml import SklearnModel
from opsml.helpers.data import create_fake_data
from opsml.scouter import SpcDriftConfig, SpcDriftProfile
from opsml.types import SaveName


def test_scouter(
    random_forest_classifier: SklearnModel,
) -> None:
    X, _ = create_fake_data(n_samples=10_000, n_features=20, n_categorical_features=4)

    model: SklearnModel = random_forest_classifier
    config = SpcDriftConfig(name="test", repository="test")
    model.create_drift_profile(X, config)

    assert isinstance(model.drift_profile, SpcDriftProfile)

    assert model.drift_profile.config.name == "test"
    assert model.drift_profile.config.repository == "test"

    for col in X.columns:
        assert col in model.drift_profile.features.keys()
        assert model.drift_profile.features[col].center is not None
        assert model.drift_profile.features[col].one_lcl is not None
        assert model.drift_profile.features[col].one_ucl is not None
        assert model.drift_profile.features[col].two_lcl is not None
        assert model.drift_profile.features[col].two_ucl is not None
        assert model.drift_profile.features[col].three_lcl is not None
        assert model.drift_profile.features[col].three_ucl is not None

    assert model.drift_profile.config.feature_map is not None

    with TemporaryDirectory() as tempdir:
        path = (Path(tempdir) / SaveName.DRIFT_PROFILE.value).with_suffix(".json")

        model.save_drift_profile(path)

        # assert path exists and empty drift profile
        assert path.exists()
        model.drift_profile = None
        assert model.drift_profile is None

        model.load_drift_profile(path)
        assert model.drift_profile is not None

        # load again
        model.load_drift_profile(path)
