use crate::{
    error::AgentError,
    genai::client::{GenAiClient, OpenAIClient},
    genai::task::Task,
    genai::types::AgentResponse,
};
use potato_head::Message;
use pyo3::prelude::*;
use std::collections::HashMap;
use tracing::debug;

#[derive(Debug, Clone)]
#[pyclass]
pub struct Agent {
    client: GenAiClient,
}

#[pymethods]
impl Agent {
    #[new]
    pub fn new(client: &Bound<'_, PyAny>) -> Result<Self, AgentError> {
        // get the client_type from the client py object
        let client: GenAiClient = if client.is_instance_of::<OpenAIClient>() {
            let extracted = client.extract::<OpenAIClient>()?;

            GenAiClient::OpenAI(extracted)
        } else {
            return Err(AgentError::ClientExtractionError(
                "Client must be an instance of OpenAIClient".to_string(),
            ));
        };
        Ok(Self { client })
    }

    pub fn execute_task(
        &self,
        task: &Task,
        context_messages: HashMap<String, Vec<Message>>,
    ) -> Result<AgentResponse, AgentError> {
        // Extract the prompt from the task
        debug!("Executing task");
        let mut user_messages = task.prompt.user_messages.clone();

        if !task.dependencies.is_empty() {
            for dep in &task.dependencies {
                if let Some(messages) = context_messages.get(dep) {
                    for message in messages {
                        // prepend the messages from dependencies
                        user_messages.insert(0, message.clone());
                    }
                }
            }
        }

        // Use the client to execute the task
        let chat_response = self.client.execute(
            &user_messages,
            &task.prompt.system_messages,
            &task.prompt.model_settings,
        )?;

        Ok(AgentResponse::new(task.id.clone(), chat_response))
    }
}
