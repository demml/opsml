use crate::agents::types::ChatResponse;
use crate::Prompt;
use opsml_utils::{create_uuid7, PyHelperFuncs};
use pyo3::prelude::*;
use serde::{
    de::{self, MapAccess, Visitor},
    ser::SerializeStruct,
    Deserialize, Deserializer, Serialize, Serializer,
};

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
}

#[pyclass]
#[derive(Debug)]
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
    pub agent_id: String,
    pub result: Option<ChatResponse>,
    #[pyo3(get)]
    pub max_retries: u32,
    pub retry_count: u32,
    pub output_type: Option<PyObject>,
}

#[pymethods]
impl Task {
    #[new]
    #[pyo3(signature = (agent_id, prompt, dependencies = None, id = None, max_retries=None))]
    pub fn new(
        agent_id: String,
        prompt: Prompt,
        dependencies: Option<Vec<String>>,
        id: Option<String>,
        max_retries: Option<u32>,
    ) -> Self {
        Self {
            prompt,
            dependencies: dependencies.unwrap_or_default(),
            status: TaskStatus::Pending,
            result: None,
            id: id.unwrap_or_else(create_uuid7),
            agent_id,
            max_retries: max_retries.unwrap_or(3),
            retry_count: 0,
            output_type: None,
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

    #[getter]
    pub fn result<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyAny>>> {
        match &self.result {
            Some(resp) => Ok(resp.to_python(py).map(Some)?),
            None => Ok(None),
        }
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

impl Task {
    pub fn increment_retry(&mut self) {
        self.retry_count += 1;
    }
}

impl Serialize for Task {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("Task", 7)?;

        // set session to none
        state.serialize_field("id", &self.id)?;
        state.serialize_field("prompt", &self.prompt)?;
        state.serialize_field("dependencies", &self.dependencies)?;
        state.serialize_field("status", &self.status)?;
        state.serialize_field("agent_id", &self.agent_id)?;
        state.serialize_field("max_retries", &self.max_retries)?;
        state.serialize_field("retry_count", &self.retry_count)?;
        state.end()
    }
}

impl FromPyObject<'_> for Task {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let id = ob.getattr("id")?;
        let prompt = ob.getattr("prompt")?.extract()?;
        let dependencies = ob.getattr("dependencies")?.extract()?;
        let status = ob.getattr("status")?.extract()?;
        let agent_id = ob.getattr("agent_id")?.extract()?;
        let result = ob.getattr("result")?.extract()?;
        let max_retries = ob.getattr("max_retries")?.extract()?;
        let retry_count = ob.getattr("retry_count")?.extract()?;

        Ok(Task {
            id,
            prompt,
            dependencies,
            status,
            agent_id,
            result,
            max_retries,
            retry_count,
            output_type: None,
        })
    }
}
