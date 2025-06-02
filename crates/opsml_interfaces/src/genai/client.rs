use crate::error::AgentError;
use crate::genai::types::ChatResponse;
use crate::genai::types::{ChatMessage, OpenAIChatRequest, OpenAIChatResponse};
use potato_head::{Message, ModelSettings};
use pyo3::prelude::*;
use reqwest::header::HeaderName;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
use reqwest::Client;

use std::collections::HashMap;
use std::str::FromStr;
use tracing::debug;

const TIMEOUT_SECS: u64 = 30;
const USER: &str = "user";
const DEVELOPER: &str = "developer";

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

#[derive(Debug, Clone)]
#[pyclass]
pub struct OpenAIClient {
    client: Client,
    api_key: String,
    base_url: String,
    #[pyo3(get)]
    client_type: ClientType,
}

#[pymethods]
impl OpenAIClient {
    #[new]
    #[pyo3(signature = (api_key, base_url = None, headers = None))]
    /// Creates a new OpenAIClient instance.
    ///
    /// # Arguments:
    /// * `api_key`: The API key for authenticating with the OpenAI API.
    /// * `base_url`: The base URL for the OpenAI API (default is the OpenAI API URL).
    /// * `headers`: Optional headers to include in the HTTP requests.
    ///
    /// # Returns:
    /// * `Result<OpenAIClient, AgentError>`: Returns an `OpenAIClient` instance on success or an `AgentError` on failure.
    pub fn new(
        api_key: Option<String>,
        base_url: Option<String>,
        headers: Option<HashMap<String, String>>,
    ) -> Result<Self, AgentError> {
        let client = build_http_client(headers)?;

        //  if optional api_key is None, check the environment variable `OPENAI_API_KEY`
        let api_key = match api_key {
            Some(key) => key,
            None => std::env::var("OPENAI_API_KEY").map_err(AgentError::EnvVarError)?,
        };

        // if optional base_url is None, use the default OpenAI API URL
        let env_base_url = std::env::var("OPENAI_API_URL").ok();
        let base_url = base_url
            .unwrap_or_else(|| env_base_url.unwrap_or_else(|| ClientUrl::OpenAI.url().to_string()));

        Ok(Self {
            client,
            api_key,
            base_url,
            client_type: ClientType::OpenAI,
        })
    }
}

impl OpenAIClient {
    /// Sends a chat completion request to the OpenAI API. This is a rust-only method
    /// that allows you to interact with the OpenAI API without needing Python.
    ///
    /// # Arguments:
    /// * `user_messages`: A slice of `Message` objects representing user messages.
    /// * `developer_messages`: A slice of `Message` objects representing developer messages.
    /// * `settings`: A reference to `ModelSettings` containing model configuration.
    ///
    /// # Returns:
    /// * `Result<ChatResponse, AgentError>`: Returns a `ChatResponse` on success or an `AgentError` on failure.
    ///
    pub async fn chat_completion(
        &self,
        user_messages: &[Message],
        developer_messages: &[Message],
        settings: &ModelSettings,
    ) -> Result<OpenAIChatResponse, AgentError> {
        let mut messages: Vec<ChatMessage> = developer_messages
            .iter()
            .map(|msg| ChatMessage {
                role: DEVELOPER.to_string(),
                content: msg.content.clone(),
            })
            .collect();

        // Add user messages to the chat
        messages.extend(user_messages.iter().map(|msg| ChatMessage {
            role: USER.to_string(),
            content: msg.content.clone(),
        }));

        // Create the OpenAI chat request
        let prompt = OpenAIChatRequest {
            model: settings.model.clone(),
            messages,
            max_completion_tokens: settings.max_tokens,
            temperature: settings.temperature,
            top_p: settings.top_p,
            frequency_penalty: settings.frequency_penalty,
            presence_penalty: settings.presence_penalty,
            parallel_tool_calls: settings.parallel_tool_calls,
            logit_bias: settings.logit_bias.clone(),
            seed: settings.seed,
        };

        // serialize the prompt to JSON
        let mut prompt = serde_json::to_value(prompt).map_err(AgentError::SerializationError)?;

        // if settings.extra_body is provided, merge it with the prompt
        if let Some(extra_body) = &settings.extra_body {
            if let (Some(prompt_obj), Some(extra_obj)) =
                (prompt.as_object_mut(), extra_body.as_object())
            {
                // Merge the extra_body fields into prompt
                for (key, value) in extra_obj {
                    prompt_obj.insert(key.clone(), value.clone());
                }
            }
        }

        let response = self
            .client
            .post(format!("{}/v1/chat/completions", self.base_url))
            .header(AUTHORIZATION, format!("Bearer {}", self.api_key))
            .json(&prompt)
            .send()
            .await
            .map_err(AgentError::RequestError)?;

        let status = response.status();
        if !status.is_success() {
            return Err(AgentError::ChatCompletionError(status));
        }

        let chat_response: OpenAIChatResponse = response.json().await?;
        debug!("Chat completion successful");

        Ok(chat_response)
    }
}

#[derive(Debug, Clone)]
pub enum GenAiClient {
    OpenAI(OpenAIClient),
}

impl GenAiClient {
    pub async fn execute(
        &self,
        user_messages: &[Message],
        developer_messages: &[Message],
        settings: &ModelSettings,
    ) -> Result<ChatResponse, AgentError> {
        match self {
            GenAiClient::OpenAI(client) => {
                let response = client
                    .chat_completion(user_messages, developer_messages, settings)
                    .await?;
                Ok(ChatResponse::OpenAI(response))
            }
        }
    }
}
