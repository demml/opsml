use ::potato_head::agents::provider::types::Provider;
use ::potato_head::{
    Agent, AudioUrl, BinaryContent, DocumentUrl, ImageUrl, Message, ModelSettings, PIIConfig,
    Prompt, PromptSanitizer, RiskLevel, SanitizationConfig, SanitizedResult, Task,
};
use opsml_interfaces::genai::workflow::{TaskList, TaskStatus, Workflow};

use pyo3::prelude::*;

#[pymodule]
pub fn potato_head(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Prompt>()?;
    m.add_class::<Message>()?;
    m.add_class::<ImageUrl>()?;
    m.add_class::<AudioUrl>()?;
    m.add_class::<DocumentUrl>()?;
    m.add_class::<BinaryContent>()?;
    m.add_class::<PIIConfig>()?;
    m.add_class::<RiskLevel>()?;
    m.add_class::<SanitizationConfig>()?;
    m.add_class::<PromptSanitizer>()?;
    m.add_class::<SanitizedResult>()?;
    m.add_class::<ModelSettings>()?;

    // agentic tools
    m.add_class::<Provider>()?;
    m.add_class::<TaskStatus>()?;
    m.add_class::<Task>()?;
    m.add_class::<TaskList>()?;
    m.add_class::<Agent>()?;
    m.add_class::<Workflow>()?;
    Ok(())
}
