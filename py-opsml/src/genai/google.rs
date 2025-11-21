use potato_head::google_types::{
    chat::{
        FunctionCallingConfig, GeminiSettings, GenerationConfig, HarmBlockMethod,
        HarmBlockThreshold, HarmCategory, LatLng, MediaResolution, Modality, Mode,
        ModelArmorConfig, PrebuiltVoiceConfig, RetrievalConfig, SafetySetting, SpeechConfig,
        ThinkingConfig, ToolConfig, VoiceConfig, VoiceConfigMode,
    },
    predict::{PredictRequest, PredictResponse},
    EmbeddingTaskType, GeminiEmbeddingConfig, GeminiEmbeddingResponse,
};
use pyo3::prelude::*;

pub fn add_google_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GenerationConfig>()?;
    m.add_class::<MediaResolution>()?;
    m.add_class::<Modality>()?;
    m.add_class::<SpeechConfig>()?;
    m.add_class::<ThinkingConfig>()?;
    m.add_class::<VoiceConfig>()?;
    m.add_class::<VoiceConfigMode>()?;
    m.add_class::<PrebuiltVoiceConfig>()?;
    m.add_class::<HarmCategory>()?;
    m.add_class::<HarmBlockMethod>()?;
    m.add_class::<HarmBlockThreshold>()?;
    m.add_class::<SafetySetting>()?;
    m.add_class::<ToolConfig>()?;
    m.add_class::<FunctionCallingConfig>()?;
    m.add_class::<RetrievalConfig>()?;
    m.add_class::<LatLng>()?;
    m.add_class::<ModelArmorConfig>()?;
    m.add_class::<Mode>()?;
    m.add_class::<GeminiSettings>()?;
    m.add_class::<GeminiEmbeddingConfig>()?;
    m.add_class::<GeminiEmbeddingResponse>()?;
    m.add_class::<PredictRequest>()?;
    m.add_class::<PredictResponse>()?;
    m.add_class::<EmbeddingTaskType>()?;
    Ok(())
}
