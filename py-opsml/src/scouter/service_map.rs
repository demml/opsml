use pyo3::prelude::*;
use scouter_client::{extract_trace_id, infer_schema, normalize_endpoint};

#[pyfunction]
fn py_normalize_endpoint(path: &str) -> String {
    normalize_endpoint(path)
}

#[pyfunction]
fn py_extract_trace_id(traceparent: &str) -> Option<String> {
    extract_trace_id(traceparent)
}

#[pyfunction]
fn py_infer_schema(body: &[u8]) -> Option<String> {
    infer_schema(body)
}

pub fn add_service_map_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_normalize_endpoint, m)?)?;
    m.add_function(wrap_pyfunction!(py_extract_trace_id, m)?)?;
    m.add_function(wrap_pyfunction!(py_infer_schema, m)?)?;
    Ok(())
}
