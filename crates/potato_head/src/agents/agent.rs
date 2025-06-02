use crate::Message;
use crate::{
    agents::client::{GenAiClient, OpenAIClient},
    agents::task::Task,
    agents::types::AgentResponse,
    error::AgentError,
};
use opsml_state::app_state;
use opsml_utils::create_uuid7;
use pyo3::prelude::*;
use std::collections::HashMap;
use tracing::debug;

#[derive(Debug, Clone)]
#[pyclass]
pub struct Agent {
    #[pyo3(get)]
    pub id: String,

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
        Ok(Self {
            client,
            id: create_uuid7(),
        })
    }

    #[pyo3(signature = (task, context_messages = HashMap::new()))]
    pub fn execute_task(
        &self,
        task: &Task,
        context_messages: HashMap<String, Vec<Message>>,
    ) -> Result<AgentResponse, AgentError> {
        // Extract the prompt from the task
        debug!("Executing task");
        let mut user_messages = task.prompt.user_message.clone();

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

        let chat_response = app_state().runtime.block_on(async {
            self.client
                .execute(
                    &user_messages,
                    &task.prompt.system_message,
                    &task.prompt.model_settings,
                )
                .await
        })?;

        Ok(AgentResponse::new(task.id.clone(), chat_response))
    }
}

/// Rust method implementation of the Agent
impl Agent {
    pub async fn execute_async_task(
        &self,
        task: &Task,
        context_messages: HashMap<String, Vec<Message>>,
    ) -> Result<AgentResponse, AgentError> {
        // Extract the prompt from the task
        debug!("Executing task: {}", task.id);
        let mut user_messages = task.prompt.user_message.clone();

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
        let chat_response = self
            .client
            .execute(
                &user_messages,
                &task.prompt.system_message,
                &task.prompt.model_settings,
            )
            .await?;

        Ok(AgentResponse::new(task.id.clone(), chat_response))
    }
}
