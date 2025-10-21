import mlflow
from sklearn.datasets import make_classification
from sklearn import ensemble  # type: ignore
import time

times = []

def run_benchmark():
    start_time = time.time()
    with mlflow.start_run() as training_run:
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

        mlflow.sklearn.log_model(
            sk_model=classifier, 
            name="random_forest", 
            input_example=X[0:10],
        )
    
    times.append(time.time() - start_time)


if __name__ == "__main__":
    for i in range(10):
        run_benchmark()

    avg_time = sum(times) / len(times)
    print(f"Average experiment run time over 10 runs: {avg_time:.4f} seconds")
