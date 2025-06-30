use opsml_state::app_state;

use potato_head::agent::Agent;
use potato_head::workflow::{Task, TaskList, Workflow};
use pyo3::{prelude::*, types::PyDict};
use serde::Deserialize;
use serde::Serialize;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::sync::RwLock;
use tracing::instrument;
use tracing::{debug, error, info, warn};

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyWorkflow {
    workflow: Workflow,

    // allow adding output types for python tasks (py only)
    // these are provided at runtime by the user and must match the response
    // format of the prompt the task is associated with
    output_types: HashMap<String, Arc<PyObject>>,
}

#[pymethods]
impl PyWorkflow {
    #[new]
    #[pyo3(signature = (name))]
    pub fn new(name: &str) -> Self {
        info!("Creating new workflow: {}", name);
        Self {
            workflow: Workflow::new(name),
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
        self.workflow.tasks.add_task(task);
    }

    pub fn add_tasks(&mut self, tasks: Vec<Task>) {
        for task in tasks {
            self.workflow.tasks.add_task(task);
        }
    }

    pub fn add_agent(&mut self, agent: &Agent) {
        self.workflow.agents.insert(agent.id.clone(), agent);
    }

    pub fn is_complete(&self) -> bool {
        self.workflow.tasks.is_complete()
    }

    pub fn pending_count(&self) -> usize {
        self.workflow.tasks.pending_count()
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
