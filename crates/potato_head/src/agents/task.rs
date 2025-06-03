use crate::agents::types::ChatResponse;
use crate::Prompt;
use opsml_utils::create_uuid7;
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

    pub result: Option<ChatResponse>,
}

#[pymethods]
impl Task {
    #[new]
    #[pyo3(signature = (prompt, dependencies = None, id = None))]
    pub fn new(prompt: Prompt, dependencies: Option<Vec<String>>, id: Option<String>) -> Self {
        Self {
            prompt,
            dependencies: dependencies.unwrap_or_default(),
            status: TaskStatus::Pending,
            result: None,
            id: id.unwrap_or_else(create_uuid7),
        }
    }

    pub fn add_dependency(&mut self, dependency: String) {
        self.dependencies.push(dependency);
    }

    pub fn set_status(&mut self, status: TaskStatus) {
        self.status = status;
    }

    pub fn set_result(&mut self, result: ChatResponse) {
        self.result = Some(result);
    }
}
