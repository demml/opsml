use potato_head::prompt::types::PromptContent;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ToolCall {
    pub id: String,
    pub type_: String,
    pub function: Value,
    pub arguments: Value,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Annotations {
    pub r#type: String,
    pub url_citations: Value,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Audio {
    pub data: String,
    pub expires_at: u64, // Unix timestamp
    pub id: String,
    pub transcript: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ChatCompletionMessage {
    pub content: Option<String>,
    pub refusal: Option<String>,
    pub role: String,
    pub annotations: Annotations,
    pub tool_calls: Vec<ToolCall>,
    pub audio: Audio,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Choice {
    pub message: ChatCompletionMessage,
    pub finish_reason: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct CompletionTokenDetails {
    pub accepted_prediction_tokens: u64,
    pub audio_tokens: u64,
    pub reasoning_tokens: u64,
    pub rejected_prediction_tokens: u64,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct PromptTokenDetails {
    pub audio_tokens: u64,
    pub cached_tokens: u64,
}

#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct Usage {
    pub completion_tokens: u64,
    pub prompt_tokens: u64,
    pub total_tokens: u64,
    pub completion_tokens_details: CompletionTokenDetails,
    pub prompt_tokens_details: PromptTokenDetails,
    pub finish_reason: String,
}

#[pyclass]
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct OpenAIChatResponse {
    pub id: String,
    pub object: String,
    pub created: u64,
    pub model: String,
    pub choices: Vec<Choice>,
    pub usage: Usage,
    pub service_tier: Option<String>,
    pub system_fingerprint: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct OpenAIChatRequest {
    pub model: String,
    pub messages: Vec<ChatMessage>,
    pub max_completion_tokens: Option<usize>,
    pub temperature: Option<f32>,
    pub top_p: Option<f32>,
    pub frequency_penalty: Option<f32>,
    pub presence_penalty: Option<f32>,
    pub parallel_tool_calls: Option<bool>,
    pub logit_bias: Option<HashMap<String, i32>>,
    pub seed: Option<u64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: PromptContent,
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ChatResponse {
    OpenAI(OpenAIChatResponse),
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
