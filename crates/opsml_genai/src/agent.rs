use crate::error::PyAgentError;
use opsml_state::app_state;
use potato_head::prompt::{parse_prompt, Message, Role};
use potato_head::workflow::Task;
use potato_head::{Agent, AgentResponse, Provider};
use pyo3::{prelude::*, IntoPyObjectExt};
use std::sync::Arc;
use tracing::debug;

#[pyclass(name = "Agent")]
#[derive(Debug, Clone)]
pub struct PyAgent {
    pub agent: Arc<Agent>,
}

#[pymethods]
impl PyAgent {
    #[new]
    #[pyo3(signature = (provider, system_message = None))]
    /// Creates a new Agent instance.
    ///
    /// # Arguments:
    /// * `provider` - A Python object representing the provider, expected to be an a variant of Provider or a string
    /// that can be mapped to a provider variant
    ///
    pub fn new(
        provider: &Bound<'_, PyAny>,
        system_message: Option<&Bound<'_, PyAny>>,
    ) -> Result<Self, PyAgentError> {
        let provider = Provider::extract_provider(provider)?;

        let system_message = if let Some(system_message) = system_message {
            Some(
                parse_prompt(system_message)?
                    .into_iter()
                    .map(|mut msg| {
                        msg.role = Role::Developer.to_string();
                        msg
                    })
                    .collect::<Vec<Message>>(),
            )
        } else {
            None
        };

        let agent = Agent::new(provider, system_message)?;

        Ok(Self {
            agent: Arc::new(agent),
        })
    }

    #[pyo3(signature = (task))]
    pub fn execute_task(&self, task: &Task) -> Result<AgentResponse, PyAgentError> {
        // Extract the prompt from the task
        debug!("Executing task");

        let chat_response = app_state()
            .runtime
            .block_on(async { self.agent.execute_async_task(&task).await })?;

        Ok(chat_response)
    }

    #[getter]
    pub fn system_message<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, PyAgentError> {
        Ok(self.agent.system_message.clone().into_bound_py_any(py)?)
    }
}
