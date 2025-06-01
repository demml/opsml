use opsml_utils::create_uuid7;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub enum TaskStatus {
    #[default]
    Pending,
    Running,
    Completed,
    Failed,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Task {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get, set)]
    pub description: String,
    #[pyo3(get, set)]
    pub dependencies: Vec<String>,
    #[pyo3(get)]
    pub status: TaskStatus,
    #[pyo3(get)]
    pub result: Option<String>,
}

#[pymethods]
impl Task {
    #[new]
    #[pyo3(signature = (description, dependencies = Vec::<String>::new(), id = None))]
    pub fn new(description: &str, dependencies: Vec<String>, id: Option<String>) -> Self {
        Self {
            id: id.unwrap_or_else(|| create_uuid7()),
            description: description.to_string(),
            dependencies,
            status: TaskStatus::Pending,
            result: None,
        }
    }

    pub fn add_dependency(&mut self, dependency: String) {
        self.dependencies.push(dependency);
    }

    pub fn set_status(&mut self, status: TaskStatus) {
        self.status = status;
    }

    pub fn set_result(&mut self, result: String) {
        self.result = Some(result);
    }
}
