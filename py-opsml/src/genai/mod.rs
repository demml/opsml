use ::potato_head::{
    prompt::settings::ModelSettings, AudioUrl, BinaryContent, ChatResponse, CompletionTokenDetails,
    DocumentUrl, EventDetails, ImageUrl, Message, Prompt, PromptTokenDetails, Provider, PyAgent,
    PyAgentResponse, PyEmbedder, PyTask, PyWorkflow, Score, Task, TaskEvent, TaskList, TaskStatus,
    Usage, WorkflowResult,
};
pub use opsml_genai::mcp::list_mcp_servers;
use opsml_types::contracts::{McpCapability, McpConfig, McpServer, McpServers, McpTransport};
pub mod google;
pub mod openai;
use pyo3::prelude::*;
use pyo3::wrap_pymodule;

#[pymodule]
pub fn genai(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Provider>()?;
    m.add_class::<PyAgent>()?;
    m.add_class::<PyWorkflow>()?;
    m.add_class::<Task>()?;
    m.add_class::<PyTask>()?;
    m.add_class::<Prompt>()?;
    m.add_class::<Message>()?;
    m.add_class::<ModelSettings>()?;
    m.add_class::<Score>()?;
    m.add_class::<AudioUrl>()?;
    m.add_class::<BinaryContent>()?;
    m.add_class::<DocumentUrl>()?;
    m.add_class::<ImageUrl>()?;
    m.add_class::<EventDetails>()?;
    m.add_class::<ChatResponse>()?;
    m.add_class::<TaskEvent>()?;
    m.add_class::<WorkflowResult>()?;
    m.add_class::<CompletionTokenDetails>()?;
    m.add_class::<PromptTokenDetails>()?;
    m.add_class::<Usage>()?;
    m.add_class::<TaskList>()?;
    m.add_class::<TaskStatus>()?;
    m.add_class::<PyAgentResponse>()?;
    m.add_class::<PyEmbedder>()?;
    m.add_wrapped(wrap_pymodule!(google::google))?;
    m.add_wrapped(wrap_pymodule!(openai::openai))?;

    // opsml specific
    m.add_function(wrap_pyfunction!(list_mcp_servers, m)?)?;
    m.add_class::<McpCapability>()?;
    m.add_class::<McpTransport>()?;
    m.add_class::<McpConfig>()?;
    m.add_class::<McpServers>()?;
    m.add_class::<McpServer>()?;
    Ok(())
}
