use crate::agents::provider::openai::OpenAIChatResponse;
use crate::{
    prompt::types::{PromptContent, Role},
    Message,
};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use crate::error::AgentError;

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ChatResponse {
    OpenAI(OpenAIChatResponse),
}

impl ChatResponse {
    pub fn is_empty(&self) -> bool {
        match self {
            ChatResponse::OpenAI(resp) => resp.choices.is_empty(),
        }
    }

    pub fn to_message(&self, role: Role) -> Result<Vec<Message>, AgentError> {
        match self {
            ChatResponse::OpenAI(resp) => {
                let first_choice = resp
                    .choices
                    .first()
                    .ok_or_else(|| AgentError::ClientNoResponseError)?;

                let message =
                    PromptContent::Str(first_choice.message.content.clone().unwrap_or_default());
                Ok(vec![Message::from(message, role)])
            }
        }
    }
}

#[pyclass]
pub struct AgentResponse {
    #[pyo3(get)]
    pub id: String,
    pub response: ChatResponse,
}

#[pymethods]
impl AgentResponse {
    #[getter]
    pub fn output(&self) -> String {
        match &self.response {
            ChatResponse::OpenAI(resp) => resp.choices.first().map_or("".to_string(), |c| {
                c.message.content.clone().unwrap_or_default()
            }),
        }
    }
}

impl AgentResponse {
    pub fn new(id: String, response: ChatResponse) -> Self {
        Self { id, response }
    }
}
