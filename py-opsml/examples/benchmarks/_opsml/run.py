from opsml.experiment import start_experiment
from opsml.card import ModelCard
from opsml.model import SklearnModel, TaskType
from sklearn.datasets import make_classification  # type: ignore
from sklearn import ensemble  # type: ignore
import time

times = []


def run_benchmark():
    start_time = time.time()
    with start_experiment(space="opsml", name="exp_basic") as exp:
        X, y = make_classification(
            n_samples=1000,
            n_features=4,
            n_informative=2,
            n_redundant=0,
            random_state=0,
            shuffle=False,
        )

        classifier = ensemble.RandomForestClassifier(n_estimators=5)
        classifier.fit(X, y)

        modelcard = ModelCard(
            interface=SklearnModel(
                model=classifier,
                sample_data=X[0:10],
                task_type=TaskType.Classification,
            ),
            space="opsml",
            name="rf_model",
        )

        exp.register_card(card=modelcard)
    times.append(time.time() - start_time)


if __name__ == "__main__":
    for i in range(10):
        run_benchmark()

    avg_time = sum(times) / len(times)
    print(f"Average experiment run time over 10 runs: {avg_time:.4f} seconds")
