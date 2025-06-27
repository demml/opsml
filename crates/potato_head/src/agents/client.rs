use crate::agents::provider::openai::OpenAIClient;
use crate::agents::types::ChatResponse;
use crate::error::AgentError;
use crate::Prompt;
use pyo3::prelude::*;
use reqwest::header::HeaderName;
use reqwest::header::{HeaderMap, HeaderValue};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::str::FromStr;

const TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone)]
#[pyclass]
pub enum ClientType {
    OpenAI,
}

pub enum ClientUrl {
    OpenAI,
}

impl ClientUrl {
    pub fn url(&self) -> &str {
        match self {
            ClientUrl::OpenAI => "https://api.openai.com",
        }
    }
}

/// Create the blocking HTTP client with optional headers.
pub fn build_http_client(
    client_headers: Option<HashMap<String, String>>,
) -> Result<Client, AgentError> {
    let mut headers = HeaderMap::new();

    if let Some(headers_map) = client_headers {
        for (key, value) in headers_map {
            headers.insert(
                HeaderName::from_str(&key).map_err(AgentError::CreateHeaderNameError)?,
                HeaderValue::from_str(&value).map_err(AgentError::CreateHeaderValueError)?,
            );
        }
    }

    let client_builder = Client::builder().timeout(std::time::Duration::from_secs(TIMEOUT_SECS));

    let client = client_builder
        .default_headers(headers)
        .build()
        .map_err(AgentError::CreateClientError)?;

    Ok(client)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum GenAiClient {
    OpenAI(OpenAIClient),
}

impl GenAiClient {
    pub async fn execute(&self, task: &Prompt) -> Result<ChatResponse, AgentError> {
        match self {
            GenAiClient::OpenAI(client) => {
                let response = client.async_chat_completion(task).await?;
                Ok(ChatResponse::OpenAI(response))
            }
        }
    }
}
