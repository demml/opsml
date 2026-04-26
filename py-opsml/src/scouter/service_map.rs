use pyo3::prelude::*;
use scouter_client::{
    extract_trace_id as extract_trace_id_impl, infer_schema as infer_schema_impl,
    normalize_endpoint as normalize_endpoint_impl,
};

#[pyfunction]
fn normalize_endpoint(path: &str) -> String {
    normalize_endpoint_impl(path)
}

#[pyfunction]
fn extract_trace_id(traceparent: &str) -> Option<String> {
    extract_trace_id_impl(traceparent)
}

#[pyfunction]
fn infer_schema(body: &[u8]) -> Option<String> {
    infer_schema_impl(body)
}

pub fn add_service_map_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(normalize_endpoint, m)?)?;
    m.add_function(wrap_pyfunction!(extract_trace_id, m)?)?;
    m.add_function(wrap_pyfunction!(infer_schema, m)?)?;
    Ok(())
}
