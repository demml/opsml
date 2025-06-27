use crate::error::AgentError;
use pyo3::prelude::*;
use reqwest::header::HeaderName;
use reqwest::header::{HeaderMap, HeaderValue};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::str::FromStr;
use tracing::error;

const TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub enum Provider {
    OpenAI,
}

impl Provider {
    pub fn url(&self) -> &str {
        match self {
            Provider::OpenAI => "https://api.openai.com",
        }
    }

    pub fn from_string(s: &str) -> Result<Self, AgentError> {
        match s.to_lowercase().as_str() {
            "openai" => Ok(Provider::OpenAI),
            _ => Err(AgentError::UnknownProviderError(s.to_string())),
        }
    }

    /// Extract provider from a PyAny object
    ///
    /// # Arguments
    /// * `provider` - PyAny object
    ///
    /// # Returns
    /// * `Result<Provider, AgentError>` - Result
    ///
    /// # Errors
    /// * `AgentError` - Error
    pub fn extract_provider(provider: &Bound<'_, PyAny>) -> Result<Provider, AgentError> {
        match provider.is_instance_of::<Provider>() {
            true => Ok(provider.extract::<Provider>().inspect_err(|e| {
                error!("Failed to extract provider: {}", e);
            })?),
            false => {
                let provider = provider.extract::<String>().unwrap();
                Ok(Provider::from_string(&provider).inspect_err(|e| {
                    error!("Failed to convert string to provider: {}", e);
                })?)
            }
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
