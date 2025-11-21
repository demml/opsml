use pyo3::prelude::*;
use scouter_client::{
    flush_tracer, get_function_type, init_tracer, shutdown_tracer, ActiveSpan, BaseTracer,
    BatchConfig, ExportConfig, FunctionType, GrpcConfig, GrpcSpanExporter, HttpSpanExporter,
    OtelHttpConfig, OtelProtocol, SpanKind, StdoutSpanExporter, TestSpanExporter,
    TraceBaggageRecord, TraceRecord, TraceSpanRecord,
};

pub fn add_tracing_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BaseTracer>()?;
    m.add_class::<ActiveSpan>()?;
    m.add_class::<SpanKind>()?;
    m.add_class::<FunctionType>()?;
    m.add_class::<ExportConfig>()?;
    m.add_class::<GrpcConfig>()?;
    m.add_class::<GrpcSpanExporter>()?;
    m.add_class::<OtelHttpConfig>()?;
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
    Ok(())
}
