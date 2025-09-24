use opsml_utils::PyHelperFuncs;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

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
    pub endpoints: Vec<String>,
    #[pyo3(get)]
    pub tags: Vec<String>,
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

#[pyclass]
struct McpIter {
    inner: std::vec::IntoIter<McpServer>,
}

#[pymethods]
impl McpIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<McpServer> {
        slf.inner.next()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct McpServers {
    pub servers: Vec<McpServer>,
}
#[pymethods]
impl McpServers {
    pub fn __getitem__(&self, index: usize) -> Option<McpServer> {
        self.servers.get(index).cloned()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<McpIter>> {
        let iter = McpIter {
            inner: slf.servers.clone().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    pub fn __len__(&self) -> usize {
        self.servers.len()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}
