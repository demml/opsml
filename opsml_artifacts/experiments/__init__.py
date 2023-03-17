# pylint: skip-file
# mypy: ignore-errors

importlib = __import__("importlib")

_optional_exp_dep_mappings = {"mlflow": "MlFlowExperiment"}
_missing_deps = []

for dep in _optional_exp_dep_mappings.keys():
    try:
        importlib.import_module(dep)
    except ImportError as _import_error:
        _missing_dep = _optional_exp_dep_mappings.pop(dep)
        _missing_deps.append(_missing_dep)

# import non-missing
for dep in _optional_exp_dep_mappings.keys():
    if dep == "mlflow":
        from opsml_artifacts.experiments.mlflow_exp import MlFlowExperiment
