use pyo3::prelude::*;
use scouter_client::{
    flush_tracer, get_current_active_span, get_function_type,
    get_tracing_headers_from_current_span, init_tracer, shutdown_tracer, ActiveSpan, BaseTracer,
    BatchConfig, FunctionType, GrpcSpanExporter, HttpSpanExporter, OtelExportConfig, OtelProtocol,
    SpanKind, StdoutSpanExporter, TestSpanExporter, TraceBaggageRecord, TraceRecord,
    TraceSpanRecord,
};

pub fn add_tracing_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BaseTracer>()?;
    m.add_class::<ActiveSpan>()?;
    m.add_class::<SpanKind>()?;
    m.add_class::<FunctionType>()?;
    m.add_class::<OtelExportConfig>()?;
    m.add_class::<GrpcSpanExporter>()?;
    m.add_class::<HttpSpanExporter>()?;
    m.add_class::<StdoutSpanExporter>()?;
    m.add_class::<OtelProtocol>()?;
    m.add_class::<TraceRecord>()?;
    m.add_class::<TraceSpanRecord>()?;
    m.add_class::<TraceBaggageRecord>()?;
    m.add_class::<TestSpanExporter>()?;
    m.add_class::<BatchConfig>()?;
    m.add_function(wrap_pyfunction!(init_tracer, m)?)?;
    m.add_function(wrap_pyfunction!(flush_tracer, m)?)?;
    m.add_function(wrap_pyfunction!(get_function_type, m)?)?;
    m.add_function(wrap_pyfunction!(shutdown_tracer, m)?)?;
    m.add_function(wrap_pyfunction!(get_tracing_headers_from_current_span, m)?)?;
    m.add_function(wrap_pyfunction!(get_current_active_span, m)?)?;
    Ok(())
}
