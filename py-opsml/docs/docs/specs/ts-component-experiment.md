# Technical Component Specification: Experiment Struct

## Overview
The `Experiment` struct serves as a core component for managing machine learning experiments in the OPSML framework, providing Python bindings through PyO3 and handling experiment lifecycle, metrics, parameters, and artifact management.

## Component Definition

```rust
#[pyclass]
pub struct Experiment {
    pub experiment: Py<PyAny>,
    pub registries: CardRegistries,
    pub hardware_queue: Option<HardwareQueue>,
    uid: String,
    artifact_key: ArtifactKey,
}
```

## Core Responsibilities

1. **Experiment Lifecycle Management**
   - Creation and initialization of experiments
   - Support for parent/child experiment relationships
   - Proper cleanup and resource management
   - Context manager support (`__enter__`/`__exit__`)

2. **Hardware Monitoring**
   - Optional hardware metrics collection
   - Background metric collection through `HardwareQueue`
   - Automatic cleanup of monitoring resources

3. **Artifact Management**
   - Code extraction and storage
   - File encryption/decryption
   - Support for single and multiple artifact logging
   - Path normalization and validation

4. **Metric and Parameter Logging**
   - Synchronous metric logging
   - Parameter logging with type safety
   - Batch logging support
   - Timestamp and step tracking

## Key Methods

### Constructor
```rust
pub fn new(
    py: Python,
    experiment: Py<PyAny>,
    registries: CardRegistries,
    log_hardware: bool,
    code_dir: Option<PathBuf>,
    experiment_uid: String,
) -> PyResult<Self>
```

### Core Operations
```rust
fn create_experiment<'py>(
    py: Python<'py>,
    space: Option<&str>,
    name: Option<&str>,
    registries: &mut CardRegistries,
    subexperiment: bool,
) -> PyResult<(Bound<'py, PyAny>, String)>

fn load_experiment<'py>(
    py: Python<'py>,
    experiment_uid: &str,
    registries: &mut CardRegistries,
) -> PyResult<Bound<'py, PyAny>>
```

### Logging Methods
```rust
pub fn log_metric(
    &self,
    name: String,
    value: f64,
    step: Option<i32>,
    timestamp: Option<i64>,
    created_at: Option<DateTime<Utc>>,
) -> PyResult<()>

pub fn log_artifact(&self, path: PathBuf) -> PyResult<()>
```

## Dependencies

- **External Crates**
  - `pyo3`: Python bindings
  - `chrono`: Time management
  - `tokio`: Async runtime
  - `tracing`: Logging and instrumentation

- **Internal Components**
  - `HardwareQueue`: Hardware metric collection
  - `CardRegistries`: Registry management
  - `OpsmlRegistry`: Registry operations
  - `ExperimentCard`: Experiment metadata

## Error Handling

- Uses `PyResult` for Python integration
- Custom error types:
  - `ExperimentError`
  - `OpsmlError`
- Debug logging for error tracking

## Thread Safety

- Uses `Arc` for shared ownership
- Safe background task management
- Proper resource cleanup

## Python Integration

### Exposed Methods
```python
# Creation
start_experiment(space=None, name=None, code_dir=None, log_hardware=False, experiment_uid=None)

# Logging
log_metric(name, value, step=None, timestamp=None, created_at=None)
log_metrics(metrics)
log_parameter(name, value)
log_parameters(parameters)
log_artifact(path)
log_artifacts(path)
```

### Context Manager Support

- The recommended way to use the `Experiment` class is through the `start_experiment` function, which returns an instance of `Experiment`.

```python
with start_experiment(...) as exp:
    exp.log_metric(...)
```

## Performance Considerations

1. **Memory Management**
   - Efficient PyObject handling
   - Proper cleanup of resources
   - Minimal cloning of data

2. **Concurrency**
   - Background hardware monitoring
   - Non-blocking operations where possible
   - Resource sharing through Arc

3. **File Operations**
   - Efficient artifact handling
   - Proper encryption/decryption
   - Stream-based file operations

## Future Considerations

1. Async logging operations
2. Enhanced hardware metrics
3. Improved artifact compression
4. Batch operation optimizations
5. Enhanced error recovery
6. Metric aggregation features

---

*Version: 1.0*  
*Last Updated: 2025-04-02*  
*Component Owner: Steven Forrester*