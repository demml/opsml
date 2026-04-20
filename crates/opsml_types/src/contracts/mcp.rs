#[cfg(feature = "python")]
use opsml_utils::PyHelperFuncs;
#[cfg(feature = "python")]
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use std::fmt::Display;

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq, Hash)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
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
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(eq, eq_int, from_py_object))]
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
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(from_py_object))]
pub struct McpConfig {
    pub capabilities: Vec<McpCapability>,
    pub transport: McpTransport,
}

impl McpConfig {
    pub fn new_rs(capabilities: Vec<McpCapability>, transport: McpTransport) -> Self {
        McpConfig {
            capabilities,
            transport,
        }
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl McpConfig {
    #[new]
    pub fn new(capabilities: Vec<McpCapability>, transport: McpTransport) -> Self {
        Self::new_rs(capabilities, transport)
    }

    #[getter]
    pub fn capabilities(&self) -> Vec<McpCapability> {
        self.capabilities.clone()
    }
    #[getter]
    pub fn transport(&self) -> McpTransport {
        self.transport.clone()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
pub struct McpServer {
    pub space: String,
    pub name: String,
    pub version: String,
    pub environment: String,
    pub urls: Vec<String>,
    pub tags: Vec<String>,
    pub config: McpConfig,
    pub description: Option<String>,
}

#[cfg(feature = "python")]
#[pymethods]
impl McpServer {
    #[getter]
    pub fn space(&self) -> String {
        self.space.clone()
    }
    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }
    #[getter]
    pub fn version(&self) -> String {
        self.version.clone()
    }
    #[getter]
    pub fn environment(&self) -> String {
        self.environment.clone()
    }
    #[getter]
    pub fn urls(&self) -> Vec<String> {
        self.urls.clone()
    }
    #[getter]
    pub fn tags(&self) -> Vec<String> {
        self.tags.clone()
    }
    #[getter]
    pub fn config(&self) -> McpConfig {
        self.config.clone()
    }
    #[getter]
    pub fn description(&self) -> Option<String> {
        self.description.clone()
    }

    pub fn __str__(&self) -> String {
        PyHelperFuncs::__str__(self)
    }
}

#[cfg(feature = "python")]
#[pyclass(skip_from_py_object)]
struct McpIter {
    inner: std::vec::IntoIter<McpServer>,
}

#[cfg(feature = "python")]
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
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
#[cfg_attr(feature = "python", pyclass(skip_from_py_object))]
pub struct McpServers {
    pub servers: Vec<McpServer>,
}

#[cfg(feature = "python")]
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
