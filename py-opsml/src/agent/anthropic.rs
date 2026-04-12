use potato_head::anthropic_types::*;
use pyo3::prelude::*;

pub fn add_anthropic_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // request types
    m.add_class::<CitationCharLocationParam>()?;
    m.add_class::<CitationPageLocationParam>()?;
    m.add_class::<CitationContentBlockLocationParam>()?;
    m.add_class::<CitationWebSearchResultLocationParam>()?;
    m.add_class::<CitationSearchResultLocationParam>()?;
    m.add_class::<TextBlockParam>()?;
    m.add_class::<Base64ImageSource>()?;
    m.add_class::<UrlImageSource>()?;
    m.add_class::<ImageBlockParam>()?;
    m.add_class::<Base64PDFSource>()?;
    m.add_class::<UrlPDFSource>()?;
    m.add_class::<PlainTextSource>()?;
    m.add_class::<CitationsConfigParams>()?;
    m.add_class::<DocumentBlockParam>()?;
    m.add_class::<SearchResultBlockParam>()?;
    m.add_class::<ThinkingBlockParam>()?;
    m.add_class::<RedactedThinkingBlockParam>()?;
    m.add_class::<ToolUseBlockParam>()?;
    m.add_class::<ToolResultBlockParam>()?;
    m.add_class::<ServerToolUseBlockParam>()?;
    m.add_class::<WebSearchResultBlockParam>()?;
    m.add_class::<WebSearchToolResultBlockParam>()?;
    m.add_class::<MessageParam>()?;
    m.add_class::<Metadata>()?;
    m.add_class::<CacheControl>()?;
    m.add_class::<Tool>()?;
    m.add_class::<ThinkingConfig>()?;
    m.add_class::<ToolChoice>()?;
    m.add_class::<AnthropicSettings>()?;
    m.add_class::<SystemPrompt>()?;

    // response types
    m.add_class::<CitationCharLocation>()?;
    m.add_class::<CitationPageLocation>()?;
    m.add_class::<CitationContentBlockLocation>()?;
    m.add_class::<CitationsWebSearchResultLocation>()?;
    m.add_class::<CitationsSearchResultLocation>()?;
    m.add_class::<TextBlock>()?;
    m.add_class::<ThinkingBlock>()?;
    m.add_class::<RedactedThinkingBlock>()?;
    m.add_class::<ToolUseBlock>()?;
    m.add_class::<ServerToolUseBlock>()?;
    m.add_class::<WebSearchResultBlock>()?;
    m.add_class::<WebSearchToolResultError>()?;
    m.add_class::<WebSearchToolResultBlock>()?;
    m.add_class::<StopReason>()?;
    m.add_class::<Usage>()?;
    m.add_class::<AnthropicMessageResponse>()?;

    Ok(())
}
