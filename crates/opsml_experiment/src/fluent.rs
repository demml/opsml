use crate::active;
use crate::error::ExperimentError;
use crate::experiment::Experiment;
use opsml_types::cards::experiment::Metric;
use pyo3::prelude::*;
use std::path::PathBuf;

/// Log a metric on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
#[pyo3(signature = (name, value, step=None, timestamp=None, created_at=None))]
pub fn log_metric(
    py: Python<'_>,
    name: String,
    value: f64,
    step: Option<i32>,
    timestamp: Option<i64>,
    created_at: Option<chrono::DateTime<chrono::Utc>>,
) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py)
        .log_metric(name, value, step, timestamp, created_at)
}

/// Log multiple metrics on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
pub fn log_metrics(py: Python<'_>, metrics: Vec<Metric>) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_metrics(metrics)
}

/// Log a parameter on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
#[pyo3(signature = (name, value))]
pub fn log_param(
    py: Python<'_>,
    name: String,
    value: Bound<'_, PyAny>,
) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_parameter(name, value)
}

/// Log multiple parameters on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
pub fn log_params(py: Python<'_>, params: Bound<'_, PyAny>) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_parameters(&params)
}

/// Log a file artifact on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
#[pyo3(signature = (lpath, rpath=None))]
pub fn log_artifact(
    py: Python<'_>,
    lpath: PathBuf,
    rpath: Option<String>,
) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_artifact(lpath, rpath)
}

/// Log a directory of artifacts on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
pub fn log_artifacts(py: Python<'_>, path: PathBuf) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_artifacts(path)
}

/// Log a Python figure on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
#[pyo3(signature = (name, figure, kwargs=None))]
pub fn log_figure(
    py: Python<'_>,
    name: String,
    figure: Bound<'_, PyAny>,
    kwargs: Option<Bound<'_, pyo3::types::PyDict>>,
) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py)
        .log_figure(py, name, &figure, kwargs.as_ref())
}

/// Log a saved figure file on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
#[pyo3(signature = (lpath, rpath=None))]
pub fn log_figure_from_path(
    py: Python<'_>,
    lpath: PathBuf,
    rpath: Option<String>,
) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow(py).log_figure_from_path(lpath, rpath)
}

/// Add one tag to the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
pub fn set_tag(py: Python<'_>, tag: String) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow_mut(py).set_tag(py, tag)
}

/// Replace tags on the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should call Experiment methods directly.
#[pyfunction]
pub fn set_tags(py: Python<'_>, tags: Vec<String>) -> Result<(), ExperimentError> {
    let exp = active::current(py)?;
    exp.borrow_mut(py).set_tags(py, tags)
}

/// Return the active experiment created by `with start_experiment(...)`.
/// Raises `NoActiveExperiment` when no experiment is active. Active state is
/// process-global and single-threaded; concurrent code should pass Experiment explicitly.
#[pyfunction]
pub fn active_experiment(py: Python<'_>) -> Result<Py<Experiment>, ExperimentError> {
    active::current(py)
}
