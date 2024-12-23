use crate::shared::{PyHelperFuncs, Suffix};
use chrono::NaiveDateTime;
use opsml_error::error::TypeError;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::fmt::Display;
use std::path::PathBuf;

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum GraphStyle {
    #[default]
    Line,
    Scatter,
}

impl Display for GraphStyle {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            GraphStyle::Line => write!(f, "line"),
            GraphStyle::Scatter => write!(f, "scatter"),
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum GraphType {
    #[default]
    Single,
    Group,
}

impl Display for GraphType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            GraphType::Single => write!(f, "single"),
            GraphType::Group => write!(f, "group"),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct CPUMetrics {
    pub cpu_percent_utilization: f64,
    pub cpu_percent_per_core: Option<Vec<f64>>,
    pub compute_overall: Option<f64>,
    pub compute_utilized: Option<f64>,
    pub load_avg: f64,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct GPUMetrics {
    pub gpu_percent_utilization: f64,
    pub gpu_percent_per_core: Option<Vec<f64>>,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct MemoryMetrics {
    pub sys_ram_total: i32,
    pub sys_ram_used: i32,
    pub sys_ram_available: i32,
    pub sys_ram_percent_used: f64,
    pub sys_swap_total: Option<i32>,
    pub sys_swap_used: Option<i32>,
    pub sys_swap_free: Option<i32>,
    pub sys_swap_percent: Option<f64>,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct NetworkRates {
    pub bytes_recv: i32,
    pub bytes_sent: i32,
}

#[derive(Serialize, Deserialize, Debug, Default, Clone)]
pub struct HardwareMetrics {
    pub cpu: CPUMetrics,
    pub memory: MemoryMetrics,
    pub network: NetworkRates,
    pub gpu: Option<GPUMetrics>,
}

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

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[pyclass]
pub struct RunGraph {
    pub name: String,
    pub x_label: String,
    pub y_label: String,
    pub x: Vec<f64>,
    pub y: Vec<f64>,
    pub y_group: HashMap<String, Vec<f64>>,
    pub graph_style: GraphStyle,
    pub graph_type: GraphType,
}

#[pymethods]
impl RunGraph {
    #[new]
    #[pyo3(signature = (name, graph_style, x_label, y_label, x, y=None, y_group=None))]
    pub fn new(
        name: String,
        graph_style: GraphStyle,
        x_label: String,
        y_label: String,
        x: Vec<f64>,
        y: Option<Vec<f64>>,
        y_group: Option<HashMap<String, Vec<f64>>>,
    ) -> anyhow::Result<Self> {
        // ensure that y_group and y are not both provided
        if y.is_some() && y_group.is_some() {
            return Err(anyhow::anyhow!(
                "y and y_group cannot both be provided. Provide only one."
            ));
        }

        let graph_type = if y.is_some() {
            // assert length of y matches length of x
            if y.as_ref().unwrap().len() != x.len() {
                return Err(anyhow::anyhow!(
                    "Length of y must match length of x. Length of y: {}, Length of x: {}",
                    y.as_ref().unwrap().len(),
                    x.len()
                ));
            }
            GraphType::Single
        } else {
            // assert length of each member of y_group matches length of x
            for (group_name, group_values) in y_group.as_ref().unwrap() {
                if group_values.len() != x.len() {
                    return Err(anyhow::anyhow!(
                        "Length of y_group member '{}' must match length of x. Length of y_group member '{}': {}, Length of x: {}",
                        group_name,
                        group_name,
                        group_values.len(),
                        x.len()
                    ));
                }
            }
            GraphType::Group
        };

        Ok(Self {
            name,
            x_label,
            y_label,
            x,
            y: y.unwrap_or_default(),
            y_group: y_group.unwrap_or_default(),
            graph_style,
            graph_type,
        })
    }
}

impl RunGraph {
    pub fn save_to_json(&self, path: Option<PathBuf>) -> Result<(), TypeError> {
        // check if path is provided
        let mut path = path.unwrap_or_default();

        // check if path is a file
        if !path.is_file() {
            // append filename to path
            let filename = format!("{}_{}{}", self.name, self.graph_style, Suffix::Json);
            path.push(filename);
        }

        PyHelperFuncs::save_to_json(self, path)
    }
}
