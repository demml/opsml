from opsml.scouter.drift import PsiDriftConfig, CustomMetric, CustomMetricDriftConfig
from opsml.scouter.alert import AlertThreshold
from opsml.model import SklearnModel
from pathlib import Path
import pandas as pd


def test_model_interface_drift_profile(
    tmp_path: Path,
    example_dataframe: pd.DataFrame,
    random_forest_classifier: SklearnModel,
):
    X, y, _, _ = example_dataframe
    model = random_forest_classifier

    # create spc
    model.create_drift_profile(X)

    # create psi
    model.create_drift_profile(X, PsiDriftConfig())

    # custom
    metric = CustomMetric(
        name="custom", value=0.5, alert_threshold=AlertThreshold.Above
    )
    model.create_drift_profile([metric], CustomMetricDriftConfig())
