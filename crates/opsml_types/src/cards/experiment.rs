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
        let cpu_percent_utilization = self.system.global_cpu_usage() as f32;
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

    pub fn get_metrics(&mut self) -> MemoryMetrics {
        self.system.refresh_memory();

        let free = self.system.free_memory() as i64;
        let total = self.system.total_memory() as i64;
        let used = self.system.used_memory() as i64;
        let available = self.system.available_memory() as i64;
        let used_percent_memory = used as f64 / total as f64;

        MemoryMetrics {
            free_memory: free,
            total_memory: total,
            used_memory: used,
            available_memory: available,
            used_percent_memory,
        }
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
            .iter()
            .map(|(_, network)| (network.received() as i64, network.transmitted() as i64))
            .fold((0, 0), |(acc_recv, acc_sent), (recv, sent)| {
                (acc_recv + recv, acc_sent + sent)
            });

        NetworkRates {
            bytes_recv,
            bytes_sent,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Default, Clone)]
pub struct HardwareMetrics {
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
            cpu: self.cpu_logger.get_metrics(),
            memory: self.memory_logger.get_metrics(),
            network: self.network_logger.get_metrics(),
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
    fn test_hardware_metrics_logger() {
        let mut logger = HardwareMetricLogger::new();
        // sleep for 5 seconds
        std::thread::sleep(std::time::Duration::from_secs(2));

        logger.get_metrics();
    }
}
