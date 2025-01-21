pub mod alert;
pub mod client;
pub mod drift;
pub mod logging;
pub mod observe;
pub mod profile;
pub mod queue;
pub mod types;

use pyo3::prelude::*;

use pyo3::wrap_pymodule;

#[pymodule]
pub fn scouter(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_wrapped(wrap_pymodule!(queue::queue))?;
    m.add_wrapped(wrap_pymodule!(logging::logging))?;
    m.add_wrapped(wrap_pymodule!(client::client))?;
    m.add_wrapped(wrap_pymodule!(drift::drift))?;
    m.add_wrapped(wrap_pymodule!(alert::alert))?;
    m.add_wrapped(wrap_pymodule!(types::types))?;
    m.add_wrapped(wrap_pymodule!(profile::profile))?;
    m.add_wrapped(wrap_pymodule!(observe::observe))?;

    Ok(())
}
