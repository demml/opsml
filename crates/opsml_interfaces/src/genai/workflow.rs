use crate::genai::{
    agent::Agent,
    task::{Task, TaskStatus},
    types::ChatResponse,
};
use opsml_utils::create_uuid7;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
#[derive(Debug, Clone)]
pub struct Workflow {
    pub id: String,
    pub name: String,
    pub tasks: HashMap<String, Task>,
    pub agents: HashMap<String, Agent>,
    pub execution_order: Vec<String>,
}

#[pymethods]
impl Workflow {
    #[new]
    #[pyo3(signature = (name))]
    pub fn new(name: String) -> Self {
        Self {
            id: create_uuid7(),
            name,
            tasks: HashMap::new(),
            agents: HashMap::new(),
            execution_order: Vec::new(),
        }
    }

    pub fn add_task(&mut self, task: Task) {
        let task_id = task.id.clone();
        self.tasks.insert(task_id.clone(), task);
        self.execution_order.push(task_id);
    }

    pub fn add_agent(&mut self, name: &str, agent: Agent) {
        self.agents.insert(name.to_string(), agent);
    }
}

impl Workflow {
    /// Iterate through all tasks and return those that are ready to be executed
    /// This also checks if all dependencies of the task are completed
    ///
    /// # Returns a vector of references to tasks that are ready to be executed
    pub fn get_ready_tasks(&self) -> Vec<&Task> {
        self.tasks
            .values()
            .filter(|task| {
                task.status == TaskStatus::Pending
                    && task.dependencies.iter().all(|dep_id| {
                        self.tasks
                            .get(dep_id)
                            .map(|dep| dep.status == TaskStatus::Completed)
                            .unwrap_or(false)
                    })
            })
            .collect()
    }

    /// Update the task with a status and optional result
    pub fn update_task_status(
        &mut self,
        task_id: &str,
        status: TaskStatus,
        result: Option<ChatResponse>,
    ) {
        if let Some(task) = self.tasks.get_mut(task_id) {
            task.status = status;
            task.result = result;
        }
    }
}
