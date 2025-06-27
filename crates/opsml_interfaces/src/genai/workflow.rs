use crate::error::WorkflowError;
use opsml_state::app_state;
use opsml_utils::create_uuid7;
use opsml_utils::json_to_pyobject;
use opsml_utils::PyHelperFuncs;
use potato_head::agents::task::PyTask;
pub use potato_head::agents::{
    agent::Agent,
    task::{Task, TaskStatus},
    types::ChatResponse,
};
use potato_head::prompt::types::Role;
use pyo3::{prelude::*, types::PyDict};
use serde::Deserialize;
use serde::Serialize;
use serde_json::json;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::sync::RwLock;
use tracing::instrument;
use tracing::{debug, error, info, warn};

#[derive(Debug)]
#[pyclass]
pub struct WorkflowResult {
    #[pyo3(get)]
    pub tasks: HashMap<String, Py<PyTask>>,
}

impl WorkflowResult {
    pub fn new(py: Python, tasks: HashMap<String, Task>) -> Self {
        let py_tasks = tasks
            .into_iter()
            .map(|(id, task)| {
                let py_task = PyTask {
                    id: task.id.clone(),
                    prompt: task.prompt,
                    dependencies: task.dependencies,
                    status: task.status,
                    agent_id: task.agent_id,
                    result: task.result,
                    max_retries: task.max_retries,
                    retry_count: task.retry_count,
                    response_type: None, // Response type is not serialized
                };
                (id, Py::new(py, py_task).unwrap())
            })
            .collect::<HashMap<_, _>>()
            .into();
        Self { tasks: py_tasks }
    }
}

#[pymethods]
impl WorkflowResult {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(&self.tasks)
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[pyclass]
pub struct TaskList {
    #[pyo3(get)]
    pub tasks: HashMap<String, Task>,
    pub execution_order: Vec<String>,
}

impl TaskList {
    pub fn new() -> Self {
        Self {
            tasks: HashMap::new(),
            execution_order: Vec::new(),
        }
    }

    pub fn is_complete(&self) -> bool {
        self.tasks
            .values()
            .all(|task| task.status == TaskStatus::Completed || task.status == TaskStatus::Failed)
    }

    pub fn add_task(&mut self, task: Task) {
        self.tasks.insert(task.id.clone(), task);
        self.rebuild_execution_order();
    }

    pub fn get_task(&self, task_id: &str) -> Option<&Task> {
        self.tasks.get(task_id)
    }

    pub fn remove_task(&mut self, task_id: &str) {
        self.tasks.remove(task_id);
    }

    pub fn pending_count(&self) -> usize {
        self.tasks
            .values()
            .filter(|task| task.status == TaskStatus::Pending)
            .count()
    }

    #[instrument(skip_all)]
    pub fn update_task_status(
        &mut self,
        task_id: &str,
        status: TaskStatus,
        result: Option<ChatResponse>,
    ) {
        debug!(status=?status, result=?result, "Updating task status");
        if let Some(task) = self.tasks.get_mut(task_id) {
            task.status = status;
            task.result = result;
        }
    }

    fn topological_sort(
        &self,
        task_id: &str,
        visited: &mut HashSet<String>,
        temp_visited: &mut HashSet<String>,
        order: &mut Vec<String>,
    ) {
        if temp_visited.contains(task_id) {
            return; // Cycle detected, skip
        }

        if visited.contains(task_id) {
            return;
        }

        temp_visited.insert(task_id.to_string());

        if let Some(task) = self.tasks.get(task_id) {
            for dep_id in &task.dependencies {
                self.topological_sort(dep_id, visited, temp_visited, order);
            }
        }

        temp_visited.remove(task_id);
        visited.insert(task_id.to_string());
        order.push(task_id.to_string());
    }

    fn rebuild_execution_order(&mut self) {
        let mut order = Vec::new();
        let mut visited = HashSet::new();
        let mut temp_visited = HashSet::new();

        for task_id in self.tasks.keys() {
            if !visited.contains(task_id) {
                self.topological_sort(task_id, &mut visited, &mut temp_visited, &mut order);
            }
        }

        self.execution_order = order;
    }

    /// Iterate through all tasks and return those that are ready to be executed
    /// This also checks if all dependencies of the task are completed
    ///
    /// # Returns a vector of references to tasks that are ready to be executed
    pub fn get_ready_tasks(&self) -> Vec<Task> {
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
            .cloned()
            .collect()
    }

    pub fn reset_failed_tasks(&mut self) -> Result<(), WorkflowError> {
        for task in self.tasks.values_mut() {
            if task.status == TaskStatus::Failed {
                task.status = TaskStatus::Pending;
                task.increment_retry();
                if task.retry_count > task.max_retries {
                    return Err(WorkflowError::MaxRetriesExceeded(task.id.clone()));
                }
            }
        }
        Ok(())
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct WorkflowRs {
    pub id: String,
    pub name: String,
    pub tasks: TaskList,
    pub agents: HashMap<String, Agent>,
}

impl WorkflowRs {
    pub fn new(name: String) -> Self {
        info!("Creating new workflow: {}", name);
        Self {
            id: create_uuid7(),
            name,
            tasks: TaskList::new(),
            agents: HashMap::new(),
        }
    }
}

/// Rust-specific implementation of a workflow
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Workflow {
    pub id: String,
    pub name: String,
    pub tasks: TaskList,
    pub agents: HashMap<String, Agent>,
}

impl Workflow {
    pub fn new(name: String) -> Self {
        info!("Creating new workflow: {}", name);
        Self {
            id: create_uuid7(),
            name,
            tasks: TaskList::new(),
            agents: HashMap::new(),
        }
    }
    pub async fn run(&self) -> Result<(), WorkflowError> {
        info!("Running workflow: {}", self.name);
        let workflow = self.clone();
        let workflow = Arc::new(RwLock::new(workflow));
        execute_workflow(workflow).await
    }

    pub fn is_complete(&self) -> bool {
        self.tasks.is_complete()
    }

    pub fn pending_count(&self) -> usize {
        self.tasks.pending_count()
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyWorkflow {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub tasks: TaskList,
    #[pyo3(get)]
    pub agents: HashMap<String, Agent>,

    // allow adding output types for python tasks (py only)
    // these are provided at runtime by the user and must match the response
    // format of the prompt the task is associated with
    output_types: HashMap<String, Arc<PyObject>>,
}

#[pymethods]
impl PyWorkflow {
    #[new]
    #[pyo3(signature = (name))]
    pub fn new(name: String) -> Self {
        info!("Creating new workflow: {}", name);
        Self {
            id: create_uuid7(),
            name,
            tasks: TaskList::new(),
            agents: HashMap::new(),
            output_types: HashMap::new(),
        }
    }

    #[pyo3(signature = (task_output_types))]
    pub fn add_task_output_types<'py>(
        &mut self,
        task_output_types: Bound<'py, PyDict>,
    ) -> PyResult<()> {
        let converted: HashMap<String, Arc<PyObject>> = task_output_types
            .iter()
            .map(|(k, v)| -> PyResult<(String, Arc<PyObject>)> {
                // Explicitly return a Result from the closure
                let key = k.extract::<String>()?;
                let value = v.clone().unbind();
                Ok((key, Arc::new(value)))
            })
            .collect::<PyResult<_>>()?;
        self.output_types.extend(converted);
        Ok(())
    }

    pub fn add_task(&mut self, task: Task) {
        self.tasks.add_task(task);
    }

    pub fn add_tasks(&mut self, tasks: Vec<Task>) {
        for task in tasks {
            self.tasks.add_task(task);
        }
    }

    pub fn add_agent(&mut self, agent: Agent) {
        self.agents.insert(agent.id.clone(), agent);
    }

    pub fn is_complete(&self) -> bool {
        self.tasks.is_complete()
    }

    pub fn pending_count(&self) -> usize {
        self.tasks.pending_count()
    }

    pub fn execution_plan<'py>(
        &self,
        py: Python<'py>,
    ) -> Result<Bound<'py, PyDict>, WorkflowError> {
        let mut remaining: HashMap<String, HashSet<String>> = self
            .tasks
            .tasks
            .iter()
            .map(|(id, task)| (id.clone(), task.dependencies.iter().cloned().collect()))
            .collect();

        let mut executed = HashSet::new();
        let mut plan = serde_json::json!({});
        let mut step = 1;

        while !remaining.is_empty() {
            // Find all tasks that can be executed in parallel
            let ready: Vec<String> = remaining
                .iter()
                .filter(|(_, deps)| deps.is_subset(&executed))
                .map(|(id, _)| id.clone())
                .collect();

            if ready.is_empty() {
                // Circular dependency detected
                break;
            }

            // Add parallel tasks to the current step
            plan[format!("step{}", step)] = serde_json::json!(ready);

            // Update tracking sets
            for task_id in &ready {
                executed.insert(task_id.clone());
                remaining.remove(task_id);
            }
            step += 1;
        }

        let pydict = PyDict::new(py);
        json_to_pyobject(py, &plan, &pydict)?;

        Ok(pydict)
    }

    pub fn run(&self, py: Python) -> Result<WorkflowResult, WorkflowError> {
        info!("Running workflow: {}", self.name);
        // Clone the workflow and pass it to the execute_workflow function
        // We do this to not modify the original workflow state
        let workflow = self.create_workflow();
        let workflow = Arc::new(RwLock::new(workflow));

        app_state()
            .runtime
            .block_on(async { execute_workflow(workflow.clone()).await })?;

        // Try to get exclusive ownership of the workflow by unwrapping the Arc if there's only one reference
        let workflow_result = match Arc::try_unwrap(workflow) {
            // If we have exclusive ownership, we can consume the RwLock
            Ok(rwlock) => {
                // Unwrap the RwLock to get the Workflow
                let workflow = rwlock
                    .into_inner()
                    .map_err(|_| WorkflowError::LockAcquireError)?;
                // Move the tasks out of the workflow
                WorkflowResult::new(py, workflow.tasks.tasks)
            }
            // If there are other references, we need to clone
            Err(arc) => {
                // Just read the workflow
                error!("Workflow still has other references, reading instead of consuming.");
                let workflow = arc
                    .read()
                    .map_err(|_| WorkflowError::ReadLockAcquireError)?;
                WorkflowResult::new(py, workflow.tasks.tasks.clone())
            }
        };

        info!("Workflow execution completed successfully.");
        Ok(workflow_result)
    }
}

impl PyWorkflow {
    fn create_workflow(&self) -> Workflow {
        Workflow {
            id: self.id.clone(),
            name: self.name.clone(),
            tasks: self.tasks.clone(),
            agents: self.agents.clone(),
        }
    }
}

/// Execute the workflow asynchronously
/// This function will be called to start the workflow execution process and does the following:
/// 1. Iterates over workflow tasks while the shared workflow is not complete.
/// 2. Gets all ready tasks
/// 3. For each ready task:
/// ///    - Marks the task as running
/// ///    - Checks previous tasks for injected context
/// ///    - Gets the agent for the task  
/// ///    - Spawn a new tokio task and execute task with agent
/// ///    - Push task to the handles vector
/// 4. Waits for all spawned tasks to complete
pub async fn execute_workflow(workflow: Arc<RwLock<Workflow>>) -> Result<(), WorkflowError> {
    // Writing notes for my own sanity :)
    // (1) Creating a shared workflow instance using Arc and RwLock
    info!(
        workflow = %workflow.read().unwrap().name,
        "Starting workflow execution"
    );

    // (2) Check if the workflow is complete
    while !workflow.read().unwrap().is_complete() {
        // (3) Rebuild the execution order of pending tasks (excluding completed tasks)
        // reset the failed tasks

        if let Err(e) = workflow.write().unwrap().tasks.reset_failed_tasks() {
            warn!("Failed to reset failed tasks: {}", e);
            return Err(e);
        }

        let ready_tasks = {
            let wf = workflow.read().unwrap();
            wf.tasks.get_ready_tasks()
        };

        info!("Found {} ready tasks for execution.", ready_tasks.len());

        if ready_tasks.is_empty() {
            // (4) If no tasks are ready, and there's still pending tasks, log a warning
            let pending_count = workflow.read().unwrap().pending_count();

            if pending_count > 0 {
                warn!("No ready tasks found but {} pending tasks remain. Possible circular dependency.", pending_count);
                break;
            }
            continue;
        }

        let mut handles = Vec::new();

        // (5) Iterate through all ready tasks and spawn an agent execution for each
        for task in ready_tasks {
            let workflow = workflow.clone();
            let task_id = task.id.clone();

            // Mark task as running
            {
                let mut wf = workflow.write().unwrap();
                wf.tasks
                    .update_task_status(&task_id, TaskStatus::Running, None);
            }

            // Build context from dependencies
            let context = {
                let wf = workflow.read().unwrap();
                let mut ctx = HashMap::new();
                for dep_id in &task.dependencies {
                    if let Some(dep) = wf.tasks.get_task(dep_id) {
                        if let Some(result) = &dep.result {
                            ctx.insert(
                                dep_id.clone(),
                                result.to_message(Role::Assistant).unwrap_or_default(),
                            );
                        }
                    }
                }
                ctx
            };

            // Get agent
            let agent = {
                let wf = workflow.read().unwrap();
                wf.agents.get(&task.agent_id).cloned()
            };

            let handle = tokio::spawn(async move {
                if let Some(agent) = agent {
                    match agent.execute_async_task(&task, context).await {
                        Ok(response) => {
                            let mut wf = workflow.write().unwrap();
                            wf.tasks.update_task_status(
                                &task_id,
                                TaskStatus::Completed,
                                Some(response.response),
                            );
                        }
                        Err(e) => {
                            error!("Task {} failed: {}", task_id, e);
                            let mut wf = workflow.write().unwrap();
                            wf.tasks
                                .update_task_status(&task_id, TaskStatus::Failed, None);
                        }
                    }
                }
            });

            handles.push(handle);
        }

        // Wait for all tasks to complete
        for handle in handles {
            if let Err(e) = handle.await {
                warn!("Task execution failed: {}", e);
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use potato_head::{prompt::types::PromptContent, Message, Prompt};

    #[test]
    fn test_workflow_creation() {
        let workflow = Workflow::new("Test Workflow".to_string());
        assert_eq!(workflow.name, "Test Workflow");
        assert_eq!(workflow.id.len(), 36); // UUID7 length
    }

    #[test]
    fn test_task_list_add_and_get() {
        let mut task_list = TaskList::new();
        let prompt_content = PromptContent::Str("Test prompt".to_string());
        let prompt = Prompt::new_rs(
            vec![Message::new_rs(prompt_content)],
            Some("gpt-4o"),
            Some("openai"),
            vec![],
            None,
            None,
            None,
        )
        .unwrap();

        let task = Task::new("task1".to_string(), prompt, None, None, None);
        task_list.add_task(task.clone());
        assert_eq!(task_list.get_task(&task.id).unwrap().id, task.id);
        task_list.reset_failed_tasks().unwrap();
    }
}
