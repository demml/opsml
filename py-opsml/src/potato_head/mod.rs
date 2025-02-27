pub mod openai;
pub mod parts;
pub mod prompts;

use pyo3::prelude::*;
use pyo3::wrap_pymodule;

#[pymodule]
pub fn potato_head(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_wrapped(wrap_pymodule!(openai::openai))?;
    m.add_wrapped(wrap_pymodule!(prompts::prompts))?;
    m.add_wrapped(wrap_pymodule!(parts::parts))?;
    Ok(())
}
