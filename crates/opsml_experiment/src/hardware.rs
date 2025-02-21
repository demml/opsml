// hardware queue for collecting runtime hardware metrics
use serde::{Deserialize, Serialize};
use sysinfo::{Networks, System};

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
    pub free_memory: u64,
    pub total_memory: u64,
    pub used_memory: u64,
    pub available_memory: u64,
    pub used_percent: f32,
}

impl GetMetrics for MemoryMetrics {
    fn get_metrics() -> Self {
        let mut system = System::new_all();
        system.refresh_memory();

        let free = system.free_memory();
        let total = system.total_memory();
        let used = system.used_memory();
        let available = system.available_memory();
        let used_percent = used as f32 / total as f32;

        MemoryMetrics {
            free_memory: free,
            total_memory: total,
            used_memory: used,
            available_memory: available,
            used_percent,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct NetworkRates {
    pub bytes_recv: u64,
    pub bytes_sent: u64,
}

impl GetMetrics for NetworkRates {
    fn get_metrics() -> Self {
        let (bytes_recv, bytes_sent) = Networks::new_with_refreshed_list()
            .iter()
            .map(|(_, network)| (network.received(), network.transmitted()))
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hardware_metrics() {
        let metrics = HardwareMetrics::get_metrics();
        // sleep for 5 seconds
        std::thread::sleep(std::time::Duration::from_secs(2));

        let metrics = HardwareMetrics::get_metrics();
    }
}
