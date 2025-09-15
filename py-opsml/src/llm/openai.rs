use potato_head::openai_types::{
    chat::{
        AllowedTools, AllowedToolsMode, AudioParam, Content, ContentPart, CustomChoice,
        CustomDefinition, CustomTool, CustomToolChoice, CustomToolFormat, FunctionChoice,
        FunctionDefinition, FunctionTool, FunctionToolChoice, Grammar, GrammarFormat,
        OpenAIChatSettings, Prediction, StreamOptions, TextFormat, Tool, ToolChoice,
        ToolChoiceMode, ToolDefinition,
    },
    embedding::{OpenAIEmbeddingConfig, OpenAIEmbeddingResponse},
};
use pyo3::prelude::*;

#[pymodule]
pub fn openai(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<AllowedTools>()?;
    m.add_class::<AudioParam>()?;
    m.add_class::<Content>()?;
    m.add_class::<ContentPart>()?;
    m.add_class::<CustomChoice>()?;
    m.add_class::<CustomDefinition>()?;
    m.add_class::<CustomTool>()?;
    m.add_class::<CustomToolChoice>()?;
    m.add_class::<CustomToolFormat>()?;
    m.add_class::<FunctionChoice>()?;
    m.add_class::<FunctionDefinition>()?;
    m.add_class::<FunctionTool>()?;
    m.add_class::<Grammar>()?;
    m.add_class::<OpenAIChatSettings>()?;
    m.add_class::<Prediction>()?;
    m.add_class::<StreamOptions>()?;
    m.add_class::<Tool>()?;
    m.add_class::<ToolChoice>()?;
    m.add_class::<ToolChoiceMode>()?;
    m.add_class::<FunctionToolChoice>()?;
    m.add_class::<ToolDefinition>()?;
    m.add_class::<AllowedToolsMode>()?;
    m.add_class::<GrammarFormat>()?;
    m.add_class::<TextFormat>()?;
    m.add_class::<OpenAIEmbeddingConfig>()?;
    m.add_class::<OpenAIEmbeddingResponse>()?;
    Ok(())
}
