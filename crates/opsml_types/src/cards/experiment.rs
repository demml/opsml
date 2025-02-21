use chrono::NaiveDateTime;
use opsml_error::TypeError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use sysinfo::{Networks, System};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metric {
    pub name: String,
    pub value: f64,
    pub step: Option<i32>,
    pub timestamp: Option<i64>,
    pub created_at: Option<NaiveDateTime>,
}

impl Default for Metric {
    fn default() -> Self {
        Self {
            name: "".to_string(),
            value: 0.0,
            step: None,
            timestamp: None,
            created_at: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    pub name: String,
    pub value: String,
    pub created_at: Option<NaiveDateTime>,
}

impl Parameter {
    pub fn new(name: String, value: String) -> Self {
        Self {
            name,
            value,
            created_at: None,
        }
    }
}

impl Default for Parameter {
    fn default() -> Self {
        Self {
            name: "".to_string(),
            value: "".to_string(),
            created_at: None,
        }
    }
}

pub trait GetMetrics {
    fn get_metrics() -> Self;
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct CPUMetrics {
    pub cpu_percent_utilization: f32,
    pub cpu_percent_per_core: Vec<f32>,
}

impl GetMetrics for CPUMetrics {
    fn get_metrics() -> Self {
        let mut system = System::new_all();
        system.refresh_cpu_all();
        let cpu_percent_utilization = system.global_cpu_usage();
        let cpu_percent_per_core = system.cpus().iter().map(|cpu| cpu.cpu_usage()).collect();
        CPUMetrics {
            cpu_percent_utilization,
            cpu_percent_per_core,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct MemoryMetrics {
    pub free_memory: i64,
    pub total_memory: i64,
    pub used_memory: i64,
    pub available_memory: i64,
    pub used_percent_memory: f32,
}

impl GetMetrics for MemoryMetrics {
    fn get_metrics() -> Self {
        let mut system = System::new_all();
        system.refresh_memory();

        let free = system.free_memory() as i64;
        let total = system.total_memory() as i64;
        let used = system.used_memory() as i64;
        let available = system.available_memory() as i64;
        let used_percent_memory = used as f32 / total as f32;

        MemoryMetrics {
            free_memory: free,
            total_memory: total,
            used_memory: used,
            available_memory: available,
            used_percent_memory,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct NetworkRates {
    pub bytes_recv: i64,
    pub bytes_sent: i64,
}

impl GetMetrics for NetworkRates {
    fn get_metrics() -> Self {
        let (bytes_recv, bytes_sent) = Networks::new_with_refreshed_list()
            .iter()
            .map(|(_, network)| (network.received() as i64, network.transmitted() as i64))
            .fold((0, 0), |(acc_recv, acc_sent), (recv, sent)| {
                (acc_recv + recv, acc_sent + sent)
            });

        // convert to kb
        let bytes_recv = bytes_recv / 1024;
        let bytes_sent = bytes_sent / 1024;

        NetworkRates {
            bytes_recv,
            bytes_sent,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct HardwareMetrics {
    pub cpu: CPUMetrics,
    pub memory: MemoryMetrics,
    pub network: NetworkRates,
}

impl GetMetrics for HardwareMetrics {
    fn get_metrics() -> Self {
        HardwareMetrics {
            cpu: CPUMetrics::get_metrics(),
            memory: MemoryMetrics::get_metrics(),
            network: NetworkRates::get_metrics(),
        }
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
    fn test_hardware_metrics() {
        let _metrics = HardwareMetrics::get_metrics();
        // sleep for 5 seconds
        std::thread::sleep(std::time::Duration::from_secs(2));

        let _metrics = HardwareMetrics::get_metrics();
    }
}
