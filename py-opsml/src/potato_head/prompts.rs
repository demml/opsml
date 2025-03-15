use ::potato_lib::{
    ChatPartAudio, ChatPartImage, ChatPartText, ChatPrompt, ImageUrl, Message, PromptType,
    RiskLevel, SanitizationConfig, SanitizationResult,
};

use pyo3::prelude::*;

#[pymodule]
pub fn prompts(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ChatPartImage>()?;
    m.add_class::<ChatPartText>()?;
    m.add_class::<ChatPrompt>()?;
    m.add_class::<ChatPartAudio>()?;
    m.add_class::<ImageUrl>()?;
    m.add_class::<Message>()?;
    m.add_class::<PromptType>()?;
    m.add_class::<RiskLevel>()?;
    m.add_class::<SanitizationConfig>()?;
    m.add_class::<SanitizationResult>()?;
    Ok(())
}
