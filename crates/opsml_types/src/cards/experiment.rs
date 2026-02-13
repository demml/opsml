use crate::error::TypeError;
use chrono::{DateTime, Utc};
use opsml_utils::PyHelperFuncs;
use pyo3::IntoPyObjectExt;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use sysinfo::{Networks, System};

use core::fmt::Debug;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass(name = "ExperimentMetric")]
#[pyo3(module = "opsml.experiment")]
pub struct Metric {
    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    pub value: f64,

    #[pyo3(get)]
    pub step: Option<i32>,

    #[pyo3(get)]
    pub timestamp: Option<i64>,

    #[pyo3(get)]
    pub created_at: Option<DateTime<Utc>>,

    #[pyo3(get)]
    pub is_eval: bool,
}

#[pymethods]
impl Metric {
    #[new]
    #[pyo3(signature = (name, value, step = None, timestamp = None, created_at = None))]
    pub fn new(
        name: String,
        value: f64,
        step: Option<i32>,
        timestamp: Option<i64>,
        created_at: Option<DateTime<Utc>>,
    ) -> Self {
        let is_eval = false;
        Self {
            name,
            value,
            step,
            timestamp,
            created_at,
            is_eval,
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl Default for Metric {
    fn default() -> Self {
        Self {
            name: "".to_string(),
            value: 0.0,
            step: None,
            timestamp: None,
            created_at: None,
            is_eval: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[pyclass]
pub struct EvalMetrics {
    #[pyo3(get)]
    pub metrics: HashMap<String, Metric>,
}

impl EvalMetrics {
    pub fn to_vec(&self) -> Vec<Metric> {
        self.metrics.values().cloned().collect()
    }
}

#[pymethods]
impl EvalMetrics {
    #[new]
    pub fn new(metrics: HashMap<String, f64>) -> Self {
        let metrics = metrics
            .into_iter()
            .map(|(name, value)| {
                (
                    name.clone(),
                    Metric {
                        name,
                        value,
                        step: None,
                        timestamp: None,
                        created_at: Some(Utc::now()),
                        is_eval: true,
                    },
                )
            })
            .collect();
        Self { metrics }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
    // make it iterable and indexable
    pub fn __getitem__(&self, key: &str) -> Result<f64, TypeError> {
        match self.metrics.get(key) {
            Some(metric) => Ok(metric.value),
            None => Err(TypeError::NotMetricFoundError(key.to_string())),
        }
    }

    pub fn __len__(&self) -> usize {
        self.metrics.len()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass(name = "ExperimentMetrics")]
#[pyo3(module = "opsml.experiment")]
pub struct Metrics {
    #[pyo3(get)]
    pub metrics: Vec<Metric>,
}

#[pyclass]
struct MetricIter {
    inner: std::vec::IntoIter<Metric>,
}

#[pymethods]
impl MetricIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<Metric> {
        slf.inner.next()
    }
}

#[pymethods]
impl Metrics {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
    // make it iterable and indexable
    pub fn __getitem__(&self, index: usize) -> Option<Metric> {
        self.metrics.get(index).cloned()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<MetricIter>> {
        let iter = MetricIter {
            inner: slf.metrics.clone().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __len__(&self) -> usize {
        self.metrics.len()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ParameterValue {
    Int(i64),
    Float(f64),
    Str(String),
}

impl ParameterValue {
    pub fn from_any(value: Bound<'_, PyAny>) -> Result<Self, TypeError> {
        if let Ok(value) = value.extract::<i64>() {
            Ok(ParameterValue::Int(value))
        } else if let Ok(value) = value.extract::<f64>() {
            Ok(ParameterValue::Float(value))
        } else if let Ok(value) = value.extract::<String>() {
            Ok(ParameterValue::Str(value))
        } else {
            Err(TypeError::InvalidType)
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
#[pyo3(module = "opsml.experiment")]
pub struct Parameter {
    #[pyo3(get)]
    pub name: String,
    pub value: ParameterValue,
}

#[pymethods]
impl Parameter {
    #[new]
    #[pyo3(signature = (name, value))]
    pub fn new(name: String, value: Bound<'_, PyAny>) -> Result<Self, TypeError> {
        let value = ParameterValue::from_any(value)?;

        Ok(Self { name, value })
    }

    #[getter]
    pub fn value<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        match &self.value {
            ParameterValue::Int(value) => Ok(value.into_bound_py_any(py)?),
            ParameterValue::Float(value) => Ok(value.into_bound_py_any(py)?),
            ParameterValue::Str(value) => Ok(value.into_bound_py_any(py)?),
        }
    }
}

impl Default for Parameter {
    fn default() -> Self {
        Self {
            name: "".to_string(),
            value: ParameterValue::Int(0),
        }
    }
}

#[pyclass]
struct ParamIter {
    inner: std::vec::IntoIter<Parameter>,
}

#[pymethods]
impl ParamIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<Parameter> {
        slf.inner.next()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
#[pyo3(module = "opsml.experiment")]
pub struct Parameters {
    #[pyo3(get)]
    pub parameters: Vec<Parameter>,
}

#[pymethods]
impl Parameters {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
    // make it iterable and indexable
    pub fn __getitem__(&self, index: usize) -> Option<Parameter> {
        self.parameters.get(index).cloned()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<ParamIter>> {
        let iter = ParamIter {
            inner: slf.parameters.clone().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __len__(&self) -> usize {
        self.parameters.len()
    }
}

pub trait GetMetrics {
    fn get_metrics() -> Self;
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct CPUMetrics {
    pub cpu_percent_utilization: f32,
    pub cpu_percent_per_core: Vec<f32>,
}

pub struct CPUMetricLogger {
    system: System,
}

impl CPUMetricLogger {
    pub fn new() -> Self {
        let mut system = System::new_all();
        system.refresh_cpu_all();
        CPUMetricLogger { system }
    }

    pub fn get_metrics(&mut self) -> CPUMetrics {
        self.system.refresh_cpu_all();
        let cpu_percent_utilization = self.system.global_cpu_usage();
        let cpu_percent_per_core = self
            .system
            .cpus()
            .iter()
            .map(|cpu| cpu.cpu_usage())
            .collect();
        CPUMetrics {
            cpu_percent_utilization,
            cpu_percent_per_core,
        }
    }
}

impl Default for CPUMetricLogger {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct MemoryMetrics {
    pub free_memory: i64,
    pub total_memory: i64,
    pub used_memory: i64,
    pub available_memory: i64,
    pub used_percent_memory: f64,
}

pub struct MemoryMetricLogger {
    system: System,
}

impl MemoryMetricLogger {
    pub fn new() -> Self {
        let mut system = System::new_all();
        system.refresh_memory();

        MemoryMetricLogger { system }
    }

    pub fn available_memory(&mut self) -> u64 {
        self.system.refresh_memory();
        self.system.total_memory() - self.system.used_memory()
    }

    pub fn get_metrics(&mut self) -> MemoryMetrics {
        self.system.refresh_memory();

        let free = self.system.free_memory() as i64;
        let total = self.system.total_memory() as i64;
        let used = self.system.used_memory() as i64;
        let available = self.system.available_memory() as i64;
        let used_percent_memory = used as f64 / total as f64 * 100.0;

        MemoryMetrics {
            free_memory: free,
            total_memory: total,
            used_memory: used,
            available_memory: available,
            used_percent_memory,
        }
    }
}

impl Default for MemoryMetricLogger {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct NetworkRates {
    pub bytes_recv: i64,
    pub bytes_sent: i64,
}

pub struct NetworkRateLogger {
    networks: Networks,
}

impl NetworkRateLogger {
    pub fn new() -> Self {
        let networks = Networks::new_with_refreshed_list();
        NetworkRateLogger { networks }
    }

    fn get_metrics(&mut self) -> NetworkRates {
        self.networks.refresh(true);

        let (bytes_recv, bytes_sent) = self
            .networks
            .values()
            .map(|network| (network.received() as i64, network.transmitted() as i64))
            .fold((0, 0), |(acc_recv, acc_sent), (recv, sent)| {
                (acc_recv + recv, acc_sent + sent)
            });

        NetworkRates {
            bytes_recv,
            bytes_sent,
        }
    }
}

impl Default for NetworkRateLogger {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct HardwareMetrics {
    pub created_at: DateTime<Utc>,
    pub cpu: CPUMetrics,
    pub memory: MemoryMetrics,
    pub network: NetworkRates,
}

pub struct HardwareMetricLogger {
    cpu_logger: CPUMetricLogger,
    memory_logger: MemoryMetricLogger,
    network_logger: NetworkRateLogger,
}

impl HardwareMetricLogger {
    pub fn new() -> Self {
        HardwareMetricLogger {
            cpu_logger: CPUMetricLogger::new(),
            memory_logger: MemoryMetricLogger::new(),
            network_logger: NetworkRateLogger::new(),
        }
    }

    pub fn get_metrics(&mut self) -> HardwareMetrics {
        HardwareMetrics {
            created_at: Utc::now(),
            cpu: self.cpu_logger.get_metrics(),
            memory: self.memory_logger.get_metrics(),
            network: self.network_logger.get_metrics(),
        }
    }
}

impl Default for HardwareMetricLogger {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct ComputeEnvironment {
    cpu_count: usize,
    total_memory: u64,
    total_swap: u64,
    system: String,
    os_version: String,
    hostname: String,
    python_version: String,
}

#[pymethods]
impl ComputeEnvironment {
    #[new]
    pub fn new(py: Python) -> Result<Self, TypeError> {
        let sys = System::new_all();

        Ok(Self {
            cpu_count: sys.cpus().len(),
            total_memory: sys.total_memory(),
            total_swap: sys.total_swap(),
            system: System::name().unwrap_or("Unknown".to_string()),
            os_version: System::os_version().unwrap_or("Unknown".to_string()),
            hostname: System::host_name().unwrap_or("Unknown".to_string()),
            python_version: py.version().to_string(),
        })
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hardware_metrics_logger() {
        let mut logger = HardwareMetricLogger::new();
        // sleep for 5 seconds
        std::thread::sleep(std::time::Duration::from_secs(2));

        logger.get_metrics();
    }
}
