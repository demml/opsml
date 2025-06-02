use crate::agents::client_types::openai::{
    OpenAIChatMessage, OpenAIChatRequest, OpenAIChatResponse,
};
use crate::agents::types::ChatResponse;
use crate::error::AgentError;
use crate::{Message, ModelSettings};
use opsml_state::app_state;
use pyo3::prelude::*;
use pyo3::IntoPyObjectExt;
use reqwest::header::HeaderName;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
use reqwest::Client;
use std::collections::HashMap;
use std::str::FromStr;
use tracing::debug;

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
    #[pyo3(signature = (api_key=None, base_url = None, headers = None))]
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
            None => {
                std::env::var("OPENAI_API_KEY").map_err(AgentError::MissingOpenAIApiKeyError)?
            }
        };

        // if optional base_url is None, use the default OpenAI API URL
        let env_base_url = std::env::var("OPENAI_API_URL").ok();
        let base_url = base_url
            .unwrap_or_else(|| env_base_url.unwrap_or_else(|| ClientUrl::OpenAI.url().to_string()));

        debug!("Creating OpenAIClient with base URL iwth key: {}", base_url);

        Ok(Self {
            client,
            api_key,
            base_url,
            client_type: ClientType::OpenAI,
        })
    }

    /// Sends a chat completion request to the OpenAI API. This is a blocking method used in python.
    /// This is only provided as a convenience method for Python users. When running with an Agent,
    /// the async version will be used instead.
    ///
    /// # Arguments:
    /// * `user_messages`: A vector of `Message` objects representing user messages.
    /// * `developer_messages`: A vector of `Message` objects representing developer messages.
    /// * `settings`: A reference to `ModelSettings` containing model configuration.
    ///
    /// # Returns:
    /// * `Result<OpenAIChatResponse, AgentError>`: Returns an `OpenAIChatResponse` on success or an `AgentError` on failure.
    pub fn chat_completion<'py>(
        &self,
        py: Python<'py>,
        user_message: Vec<Message>,
        developer_message: Vec<Message>,
        settings: &ModelSettings,
    ) -> Result<Bound<'py, PyAny>, AgentError> {
        let resp = app_state().runtime.block_on(async {
            self.async_chat_completion(&user_message, &developer_message, settings)
                .await
        })?;
        Ok(resp.into_bound_py_any(py)?)
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
    pub async fn async_chat_completion(
        &self,
        user_message: &[Message],
        developer_message: &[Message],
        settings: &ModelSettings,
    ) -> Result<OpenAIChatResponse, AgentError> {
        let mut messages: Vec<OpenAIChatMessage> = developer_message
            .iter()
            .map(OpenAIChatMessage::from_message)
            .collect::<Result<Vec<_>, _>>()?;

        // Add user messages to the chat
        messages.extend(
            user_message
                .iter()
                .map(OpenAIChatMessage::from_message)
                .collect::<Result<Vec<_>, _>>()?,
        );

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

        debug!(
            "Sending chat completion request to OpenAI API: {:?}",
            prompt
        );

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
            // print the response body for debugging
            let body = response
                .text()
                .await
                .unwrap_or_else(|_| "No response body".to_string());
            return Err(AgentError::ChatCompletionError(body, status));
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
                    .async_chat_completion(user_messages, developer_messages, settings)
                    .await?;
                Ok(ChatResponse::OpenAI(response))
            }
        }
    }
}
