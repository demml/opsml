# type: ignore

from typing import Tuple
from scouter import DriftConfig, DriftProfile
import pandas as pd
from opsml import SklearnModel
from opsml.helpers.data import create_fake_data


def test_scouter(
    random_forest_classifier: SklearnModel,
    example_dataframe: Tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ],
) -> None:
    # X, _, _, _ = example_dataframe
    X, _ = create_fake_data(n_samples=10_000, n_features=20, n_categorical_features=4)

    model: SklearnModel = random_forest_classifier
    config = DriftConfig(name="test", repository="test")
    model.create_drift_profile(X, config)

    assert isinstance(model.drift_profile, DriftProfile)

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
