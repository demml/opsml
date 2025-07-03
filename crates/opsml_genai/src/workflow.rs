/// Python workflows are a work in progress
use crate::{agent::PyAgent, error::PyWorkflowError};
use opsml_state::app_state;
use potato_head::execute_workflow;
use potato_head::json_to_pyobject;
use potato_head::prompt::parse_response_format;
use potato_head::workflow::{Task, Workflow, WorkflowResult};
use pyo3::{prelude::*, types::PyDict};
use std::collections::HashMap;
use std::sync::Arc;
use std::sync::RwLock;
use tracing::{debug, error, info};

#[pyclass(name = "Workflow")]
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

    #[pyo3(signature = (task, output_type = None))]
    pub fn add_task(
        &mut self,
        py: Python<'_>,
        mut task: Task,
        output_type: Option<Bound<'_, PyAny>>,
    ) -> Result<(), PyWorkflowError> {
        if let Some(output_type) = output_type {
            // Parse and set the response format
            task.prompt.response_format =
                parse_response_format(py, &output_type).map_err(|_| {
                    PyWorkflowError::InvalidOutputType(
                        "Invalid output type provided for task".to_string(),
                    )
                })?;

            // Store the output type for later use
            self.output_types
                .insert(task.id.clone(), Arc::new(output_type.unbind()));
        }

        self.workflow.tasks.add_task(task)?;
        Ok(())
    }

    pub fn add_tasks(&mut self, tasks: Vec<Task>) -> Result<(), PyWorkflowError> {
        for task in tasks {
            self.workflow.tasks.add_task(task)?;
        }
        Ok(())
    }

    pub fn add_agent(&mut self, agent: &Bound<'_, PyAgent>) {
        // extract the arc rust agent from the python agent
        let agent = agent.extract::<PyAgent>().unwrap().agent.clone();
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
    ) -> Result<Bound<'py, PyDict>, PyWorkflowError> {
        let plan = self.workflow.execution_plan()?;
        debug!("Execution plan: {:?}", plan);

        // turn hashmap into a to json
        let json = serde_json::to_value(plan).map_err(|e| {
            error!("Failed to serialize execution plan to JSON: {}", e);
            PyWorkflowError::SerializationError(e)
        })?;

        let pydict = PyDict::new(py);
        json_to_pyobject(py, &json, &pydict)?;

        Ok(pydict)
    }

    pub fn run(&self, py: Python) -> Result<WorkflowResult, PyWorkflowError> {
        info!("Running workflow: {}", self.workflow.name);
        // Clone the workflow and pass it to the execute_workflow function
        // We do this to not modify the original workflow state
        let workflow = self.create_workflow_arc();

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
                    .map_err(|_| PyWorkflowError::LockAcquireError)?;
                // Move the tasks out of the workflow
                WorkflowResult::new(
                    py,
                    workflow.tasks.tasks,
                    &self.output_types,
                    workflow.event_tracker.events,
                )
            }
            // If there are other references, we need to clone
            Err(arc) => {
                // Just read the workflow
                error!("Workflow still has other references, reading instead of consuming.");
                let workflow = arc
                    .read()
                    .map_err(|_| PyWorkflowError::ReadLockAcquireError)?;
                WorkflowResult::new(
                    py,
                    workflow.tasks.tasks.clone(),
                    &self.output_types,
                    workflow.event_tracker.events.clone(),
                )
            }
        };

        info!("Workflow execution completed successfully.");
        Ok(workflow_result)
    }
}

impl PyWorkflow {
    pub fn create_workflow_arc(&self) -> Arc<RwLock<Workflow>> {
        Arc::new(RwLock::new(self.workflow.clone()))
    }
}
