use crate::error::PyAgentError;
use potato_head::agent::agents::provider::types::Provider;
use potato_head::agent::agents::types::AgentResponse;
use potato_head::agent::Agent;
use potato_head::prompt::prompt::{parse_prompt, Message, Role};
use potato_head::workflow::Task;
use pyo3::prelude::*;
use tracing::debug;

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyAgent {
    pub agent: Agent,
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

        let agent = Agent::new(provider, system_message).map_err(|e| PyAgentError::from(e))?;

        Ok(Self { agent })
    }

    #[pyo3(signature = (task))]
    pub fn execute_task(&self, task: &Task) -> Result<AgentResponse, PyAgentError> {
        // Extract the prompt from the task
        debug!("Executing task");
        // we need to clone in order to not modify the original task
        let mut prompt = task.clone().prompt;

        // Combine system messages, with agent messages taking precedence
        if !self.agent.system_message.is_empty() {
            let mut combined_messages = self.agent.system_message.clone();
            combined_messages.extend(prompt.system_message);
            prompt.system_message = combined_messages;
        }

        let chat_response = app_state()
            .runtime
            .block_on(async { self.client.execute(&prompt).await })?;

        Ok(AgentResponse::new(task.id.clone(), chat_response))
    }
}
