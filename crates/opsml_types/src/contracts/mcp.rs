use crate::error::TypeError;
use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt::Display;

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
#[pyclass]
pub enum McpTransport {
    #[serde(alias = "HTTP", alias = "http")]
    Http,
    #[serde(alias = "STDIO", alias = "stdio")]
    Stdio,
}

impl Display for McpTransport {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            McpTransport::Http => write!(f, "Http"),
            McpTransport::Stdio => write!(f, "Stdio"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
#[pyclass]
pub enum McpCapability {
    #[serde(alias = "RESOURCES", alias = "resources")]
    Resources,
    #[serde(alias = "TOOLS", alias = "tools")]
    Tools,
    #[serde(alias = "PROMPTS", alias = "prompts")]
    Prompts,
}

impl Display for McpCapability {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            McpCapability::Resources => write!(f, "Resources"),
            McpCapability::Tools => write!(f, "Tools"),
            McpCapability::Prompts => write!(f, "Prompts"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct McpConfig {
    #[pyo3(get)]
    pub capabilities: Vec<McpCapability>,
    #[pyo3(get)]
    pub transport: McpTransport,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct McpServer {
    #[pyo3(get)]
    pub space: String,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub version: String,
    #[pyo3(get)]
    pub environment: String,
    #[pyo3(get)]
    pub endpoint: String,
    #[pyo3(get)]
    pub config: McpConfig,
    #[pyo3(get)]
    pub description: Option<String>,
}

#[pymethods]
impl McpServer {
    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct McpServers {
    servers: HashMap<String, McpServer>,
}
#[pymethods]
impl McpServers {
    pub fn __getitem__(&self, key: &str) -> Result<McpServer, TypeError> {
        match self.servers.get(key) {
            Some(server) => Ok(server.clone()),
            None => Err(TypeError::McpServerNotFound(key.to_string())),
        }
    }

    pub fn __len__(&self) -> usize {
        self.servers.len()
    }
}
