use scouter_client::potato_head::prelude::{
    prompt_types::*, EventDetails, Provider, PyAgent, PyAgentResponse, PyEmbedder, PyWorkflow,
    Task, TaskEvent, TaskList, TaskStatus, WorkflowResult, WorkflowTask,
};
pub mod anthropic;
pub mod google;
pub mod mcp;
pub mod openai;
use pyo3::prelude::*;

pub fn add_agent_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // prompt interface
    m.add_class::<Prompt>()?;
    m.add_class::<Role>()?;
    m.add_class::<ModelSettings>()?;
    m.add_class::<Provider>()?;
    m.add_class::<Score>()?;
    m.add_class::<ResponseType>()?;

    // workflow
    m.add_class::<TaskEvent>()?;
    m.add_class::<EventDetails>()?;
    m.add_class::<WorkflowResult>()?;
    m.add_class::<PyWorkflow>()?;
    m.add_class::<WorkflowTask>()?;
    m.add_class::<TaskList>()?;

    // agents
    m.add_class::<PyAgent>()?;
    m.add_class::<Task>()?;
    m.add_class::<TaskStatus>()?;
    m.add_class::<PyAgentResponse>()?;
    m.add_class::<PyEmbedder>()?;
    m.add_function(wrap_pyfunction!(mcp::list_mcp_servers, m)?)?;
    anthropic::add_anthropic_module(m)?;
    google::add_google_module(m)?;
    openai::add_openai_module(m)?;
    Ok(())
}
