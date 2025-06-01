use opsml_utils::create_uuid7;
use potato_head::Prompt;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Task {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get, set)]
    pub prompt: Prompt,
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
    #[pyo3(signature = (prompt, dependencies = Vec::<String>::new(), id = None))]
    pub fn new(prompt: Prompt, dependencies: Vec<String>, id: Option<String>) -> Self {
        Self {
            id: id.unwrap_or_else(|| create_uuid7()),
            prompt,
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
