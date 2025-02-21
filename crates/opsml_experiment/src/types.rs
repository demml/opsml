use chrono::NaiveDateTime;
use opsml_error::TypeError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use sysinfo::System;

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
