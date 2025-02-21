use opsml_experiment::{start_experiment, Experiment};

use pyo3::prelude::*;

#[pymodule]
pub fn experiment(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Experiment>()?;
    m.add_function(wrap_pyfunction!(start_experiment, m)?)?;
    Ok(())
}
