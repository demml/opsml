"""
OpsML Getting Started

Prerequisites:
  pip install opsml scikit-learn

Run:
  1. Start the server:  opsml ui start
  2. Run this script:   python py-opsml/examples/getting_started.py
  3. Open the UI:       http://localhost:3000 (guest / guest)
  4. Stop the server:   opsml ui stop
"""

from opsml import DataCard, ModelCard, SklearnModel, TaskType
from opsml.data import PandasData
from opsml.experiment import start_experiment
from opsml.helpers.data import create_fake_data
from sklearn import ensemble  # type: ignore
from pathlib import Path

SPACE = "getting-started"

_PARENT_DIR = Path(__file__).parent


X, y = create_fake_data(n_samples=1000)

with start_experiment(space=SPACE, name="quickstart") as exp:
    # DataCard
    data_card = DataCard(
        space=SPACE,
        name="sample-data",
        interface=PandasData(X),
    )
    exp.register_card(data_card)
    print(f"DataCard:      v{data_card.version}  uid={data_card.uid}")

    # ModelCard
    classifier = ensemble.RandomForestClassifier(n_estimators=10, random_state=42)
    classifier.fit(X.to_numpy(), y.to_numpy().ravel())

    model_card = ModelCard(
        space=SPACE,
        name="classifier",
        interface=SklearnModel(
            model=classifier,
            sample_data=X[:10],
            task_type=TaskType.Classification,
        ),
    )
    exp.register_card(model_card)
    print(f"ModelCard:     v{model_card.version}  uid={model_card.uid}")

    # Log metrics and parameters
    exp.log_metric("accuracy", 0.91, step=0)
    exp.log_parameter("n_estimators", 10)

    artifact_path = _PARENT_DIR / "genai"
    print(f"Logging artifact: {artifact_path}")

    exp.log_artifacts(artifact_path)  # log all files in the genai directory as artifacts

print(f"\nOpen http://localhost:3000 to browse registered cards.")
