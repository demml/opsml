use potato_head::openai_types::*;
use pyo3::prelude::*;

pub fn add_openai_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // settings
    m.add_class::<AudioParam>()?;
    m.add_class::<PredictionContentPart>()?;
    m.add_class::<Content>()?;
    m.add_class::<Prediction>()?;
    m.add_class::<StreamOptions>()?;
    m.add_class::<ToolChoiceMode>()?;
    m.add_class::<FunctionChoice>()?;
    m.add_class::<FunctionToolChoice>()?;
    m.add_class::<CustomChoice>()?;
    m.add_class::<CustomToolChoice>()?;
    m.add_class::<ToolDefinition>()?;
    m.add_class::<AllowedToolsMode>()?;
    m.add_class::<InnerAllowedTools>()?;
    m.add_class::<AllowedTools>()?;
    m.add_class::<ToolChoice>()?;
    m.add_class::<FunctionDefinition>()?;
    m.add_class::<FunctionTool>()?;
    m.add_class::<TextFormat>()?;
    m.add_class::<Grammar>()?;
    m.add_class::<GrammarFormat>()?;
    m.add_class::<CustomToolFormat>()?;
    m.add_class::<CustomDefinition>()?;
    m.add_class::<CustomTool>()?;
    m.add_class::<Tool>()?;
    m.add_class::<OpenAIChatSettings>()?;

    // request types
    m.add_class::<File>()?;
    m.add_class::<FileContentPart>()?;
    m.add_class::<InputAudioData>()?;
    m.add_class::<InputAudioContentPart>()?;
    m.add_class::<ImageUrl>()?;
    m.add_class::<ImageContentPart>()?;
    m.add_class::<TextContentPart>()?;
    m.add_class::<ChatMessage>()?;

    // response type
    m.add_class::<Function>()?;
    m.add_class::<ToolCall>()?;
    m.add_class::<UrlCitation>()?;
    m.add_class::<Annotations>()?;
    m.add_class::<Audio>()?;
    m.add_class::<ChatCompletionMessage>()?;
    m.add_class::<TopLogProbs>()?;
    m.add_class::<LogContent>()?;
    m.add_class::<LogProbs>()?;
    m.add_class::<Choice>()?;
    m.add_class::<CompletionTokenDetails>()?;
    m.add_class::<PromptTokenDetails>()?;
    m.add_class::<Usage>()?;
    m.add_class::<OpenAIChatResponse>()?;

    // embedding types
    m.add_class::<OpenAIEmbeddingConfig>()?;
    m.add_class::<EmbeddingObject>()?;
    m.add_class::<UsageObject>()?;
    m.add_class::<OpenAIEmbeddingResponse>()?;

    Ok(())
}
