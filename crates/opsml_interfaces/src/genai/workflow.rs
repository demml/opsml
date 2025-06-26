use crate::error::WorkflowError;
use opsml_state::app_state;
use opsml_utils::create_uuid7;
use opsml_utils::json_to_pyobject;
pub use potato_head::agents::{
    agent::Agent,
    task::{Task, TaskStatus},
    types::ChatResponse,
};
use potato_head::prompt::types::Role;
use pyo3::{prelude::*, types::PyDict};
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::sync::RwLock;
use tracing::{error, info, warn};

#[derive(Debug, Clone, Default)]
#[pyclass]
pub struct TaskList {
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
pub struct Workflow {
    #[pyo3(get)]
    pub id: String,

    #[pyo3(get)]
    pub name: String,

    #[pyo3(get)]
    pub tasks: TaskList,

    #[pyo3(get)]
    pub agents: HashMap<String, Agent>,
}

#[pymethods]
impl Workflow {
    #[new]
    #[pyo3(signature = (name))]
    pub fn new(name: String) -> Self {
        Self {
            id: create_uuid7(),
            name,
            tasks: TaskList::new(),
            agents: HashMap::new(),
        }
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

    pub fn run(&self) -> Result<(), WorkflowError> {
        info!("Running workflow: {}", self.name);
        // Here you would implement the logic to run the workflow
        // clone the workflow and pass it to the execute_workflow function
        let workflow = self.clone();
        let workflow = Arc::new(RwLock::new(workflow));
        app_state()
            .runtime
            .block_on(async { execute_workflow(workflow).await })?;

        info!("Workflow execution completed successfully.");
        Ok(())
    }
}

// Rust-specific
impl Workflow {
    pub async fn run_rs(&self) -> Result<(), WorkflowError> {
        info!("Running workflow: {}", self.name);
        let workflow = self.clone();
        let workflow = Arc::new(RwLock::new(workflow));
        execute_workflow(workflow).await
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
        "Starting workflow execution: {}",
        workflow.read().unwrap().name
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
