use opsml_experiment::{
    get_experiment_metrics, get_experiment_parameters, start_experiment, Experiment,
};
use opsml_types::cards::experiment::{Metric, Parameter};
use pyo3::prelude::*;

#[pymodule]
pub fn experiment(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Experiment>()?;
    m.add_class::<Metric>()?;
    m.add_class::<Parameter>()?;
    m.add_function(wrap_pyfunction!(get_experiment_metrics, m)?)?;
    m.add_function(wrap_pyfunction!(get_experiment_parameters, m)?)?;
    m.add_function(wrap_pyfunction!(start_experiment, m)?)?;
    Ok(())
}
