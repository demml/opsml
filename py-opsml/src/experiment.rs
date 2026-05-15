use opsml_experiment::{
    download_artifact, fluent, get_experiment_metrics, get_experiment_parameters, start_experiment,
    Experiment,
};
use opsml_types::cards::experiment::{
    ExperimentEvalMetrics, Metric, Metrics, Parameter, Parameters,
};
use pyo3::prelude::*;

pub fn add_experiment_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Experiment>()?;
    m.add_class::<Metric>()?;
    m.add_class::<Parameter>()?;
    m.add_class::<Parameters>()?;
    m.add_class::<Metrics>()?;
    m.add_class::<ExperimentEvalMetrics>()?;
    m.add_function(wrap_pyfunction!(get_experiment_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(get_experiment_parameters, m)?)?;
    m.add_function(wrap_pyfunction!(download_artifact, m)?)?;
    m.add_function(wrap_pyfunction!(start_experiment, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_metric, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_param, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_params, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_artifact, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_artifacts, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_figure, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::log_figure_from_path, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::set_tag, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::set_tags, m)?)?;
    m.add_function(wrap_pyfunction!(fluent::active_experiment, m)?)?;
    Ok(())
}
