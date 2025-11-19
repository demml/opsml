One of the benefits of using OpsML is its performance and simplified dependency chain compared to other python-based MLOps frameworks like `MLflow`. While we are continually working on adding additional benchmarks, below are some initial performance comparisons between OpsML and MLflow.

## Benchmark Setup
See the [benchmark setup documentation](https://github.com/demml/opsml/tree/main/py-opsml/examples) for the current benchmark setup.

For the results below, we created a separate virtual environment for each framework with only the required dependencies installed + scikit-learn. We then ran the same benchmark script for each framework to compare performance.


## Benchmark Results

The following table summarizes the benchmark results comparing OpsML and MLflow for a simple model training and logging task using scikit-learn. **Note** - this tests both frameworks running in server mode (local storage + sqlite).

| Framework | Time Taken (seconds) | Dependencies | Venv size (MB) |
|-----------|----------------------|--------------------|------------------|
| OpsML     | 0.027                | 9                  | 321  (opsml - 25 (includes server deps)) |
| MLflow    | 1.2                  | 116                | 501             |