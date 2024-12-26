use opsml_error::error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::PyType;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::fmt::Display;

#[pyclass]
#[derive(Debug)]
#[allow(dead_code)]
pub struct HuggingFaceOnnxArgs {
    #[pyo3(get)]
    pub ort_type: HuggingFaceORTModel,

    #[pyo3(get)]
    pub provider: String,

    #[pyo3(get)]
    pub quantize: bool,

    #[pyo3(get)]
    pub config: Option<PyObject>,
}

#[pymethods]
impl HuggingFaceOnnxArgs {
    #[new]
    #[pyo3(signature = (ort_type, provider=None, quantize=false, config=None))]
    pub fn new(
        py: Python,
        ort_type: HuggingFaceORTModel,
        provider: Option<String>,
        quantize: Option<bool>,
        config: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Self> {
        // check if ort_type is valid (does it match any of the HuggingFaceORTModel enum variants?)

        let config = HuggingFaceOnnxArgs::check_optimum_config(py, config)?;

        Ok(HuggingFaceOnnxArgs {
            ort_type,
            provider: provider.unwrap_or_else(|| "CPUExecutionProvider".to_string()),
            quantize: quantize.unwrap_or(false),
            config,
        })
    }
}

impl HuggingFaceOnnxArgs {
    fn check_optimum_config(
        py: Python,
        config: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Option<PyObject>> {
        if config.is_none() {
            return Ok(None);
        }

        let config = config.unwrap();

        // Import the necessary classes from the optimum.onnxruntime module
        let optimum_module = py.import("optimum.onnxruntime")?;
        let auto_quantization_config_attr = optimum_module.getattr("AutoQuantizationConfig")?;
        let auto_quantization_config = auto_quantization_config_attr
            .downcast::<PyType>()
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        let ort_config_attr = optimum_module.getattr("ORTConfig")?;
        let ort_config = ort_config_attr
            .downcast::<PyType>()
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        let quantization_config_attr = optimum_module.getattr("QuantizationConfig")?;
        let quantization_config = quantization_config_attr
            .downcast::<PyType>()
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        // Assert that config is an instance of one of the specified classes
        let is_valid_config = config.is_instance(auto_quantization_config)?
            || config.is_instance(ort_config)?
            || config.is_instance(quantization_config)?;

        if !is_valid_config {
            return Err(OpsmlError::new_err(
                "config must be an instance of AutoQuantizationConfig, ORTConfig, or QuantizationConfig".to_string(),
            ));
        }

        Ok(Some(
            config
                .into_py_any(py)
                .map_err(|e| OpsmlError::new_err(e.to_string()))?,
        ))
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceTask {
    AudioClassification,
    AutomaticSpeechRecognition,
    Conversational,
    DepthEstimation,
    DocumentQuestionAnswering,
    FeatureExtraction,
    FillMask,
    ImageClassification,
    ImageSegmentation,
    ImageToImage,
    ImageToText,
    MaskGeneration,
    ObjectDetection,
    QuestionAnswering,
    Summarization,
    TableQuestionAnswering,
    Text2TextGeneration,
    TextClassification,
    TextGeneration,
    TextToAudio,
    TokenClassification,
    Translation,
    TranslationXxToYy,
    VideoClassification,
    VisualQuestionAnswering,
    ZeroShotClassification,
    ZeroShotImageClassification,
    ZeroShotAudioClassification,
    ZeroShotObjectDetection,
}

#[pymethods]
impl HuggingFaceTask {
    fn __str__(&self) -> String {
        match self {
            HuggingFaceTask::AudioClassification => "audio-classification".to_string(),
            HuggingFaceTask::AutomaticSpeechRecognition => {
                "automatic-speech-recognition".to_string()
            }
            HuggingFaceTask::Conversational => "conversational".to_string(),
            HuggingFaceTask::DepthEstimation => "depth-estimation".to_string(),
            HuggingFaceTask::DocumentQuestionAnswering => "document-question-answering".to_string(),
            HuggingFaceTask::FeatureExtraction => "feature-extraction".to_string(),
            HuggingFaceTask::FillMask => "fill-mask".to_string(),
            HuggingFaceTask::ImageClassification => "image-classification".to_string(),
            HuggingFaceTask::ImageSegmentation => "image-segmentation".to_string(),
            HuggingFaceTask::ImageToImage => "image-to-image".to_string(),
            HuggingFaceTask::ImageToText => "image-to-text".to_string(),
            HuggingFaceTask::MaskGeneration => "mask-generation".to_string(),
            HuggingFaceTask::ObjectDetection => "object-detection".to_string(),
            HuggingFaceTask::QuestionAnswering => "question-answering".to_string(),
            HuggingFaceTask::Summarization => "summarization".to_string(),
            HuggingFaceTask::TableQuestionAnswering => "table-question-answering".to_string(),
            HuggingFaceTask::Text2TextGeneration => "text2text-generation".to_string(),
            HuggingFaceTask::TextClassification => "text-classification".to_string(),
            HuggingFaceTask::TextGeneration => "text-generation".to_string(),
            HuggingFaceTask::TextToAudio => "text-to-audio".to_string(),
            HuggingFaceTask::TokenClassification => "token-classification".to_string(),
            HuggingFaceTask::Translation => "translation".to_string(),
            HuggingFaceTask::TranslationXxToYy => "translation_xx_to_yy".to_string(),
            HuggingFaceTask::VideoClassification => "video-classification".to_string(),
            HuggingFaceTask::VisualQuestionAnswering => "visual-question-answering".to_string(),
            HuggingFaceTask::ZeroShotClassification => "zero-shot-classification".to_string(),
            HuggingFaceTask::ZeroShotImageClassification => {
                "zero-shot-image-classification".to_string()
            }
            HuggingFaceTask::ZeroShotAudioClassification => {
                "zero-shot-audio-classification".to_string()
            }
            HuggingFaceTask::ZeroShotObjectDetection => "zero-shot-object-detection".to_string(),
        }
    }
}
impl Display for HuggingFaceTask {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            HuggingFaceTask::AudioClassification => write!(f, "audio-classification"),
            HuggingFaceTask::AutomaticSpeechRecognition => {
                write!(f, "automatic-speech-recognition")
            }
            HuggingFaceTask::Conversational => write!(f, "conversational"),
            HuggingFaceTask::DepthEstimation => write!(f, "depth-estimation"),
            HuggingFaceTask::DocumentQuestionAnswering => write!(f, "document-question-answering"),
            HuggingFaceTask::FeatureExtraction => write!(f, "feature-extraction"),
            HuggingFaceTask::FillMask => write!(f, "fill-mask"),
            HuggingFaceTask::ImageClassification => write!(f, "image-classification"),
            HuggingFaceTask::ImageSegmentation => write!(f, "image-segmentation"),
            HuggingFaceTask::ImageToImage => write!(f, "image-to-image"),
            HuggingFaceTask::ImageToText => write!(f, "image-to-text"),
            HuggingFaceTask::MaskGeneration => write!(f, "mask-generation"),
            HuggingFaceTask::ObjectDetection => write!(f, "object-detection"),
            HuggingFaceTask::QuestionAnswering => write!(f, "question-answering"),
            HuggingFaceTask::Summarization => write!(f, "summarization"),
            HuggingFaceTask::TableQuestionAnswering => write!(f, "table-question-answering"),
            HuggingFaceTask::Text2TextGeneration => write!(f, "text2text-generation"),
            HuggingFaceTask::TextClassification => write!(f, "text-classification"),
            HuggingFaceTask::TextGeneration => write!(f, "text-generation"),
            HuggingFaceTask::TextToAudio => write!(f, "text-to-audio"),
            HuggingFaceTask::TokenClassification => write!(f, "token-classification"),
            HuggingFaceTask::Translation => write!(f, "translation"),
            HuggingFaceTask::TranslationXxToYy => write!(f, "translation_xx_to_yy"),
            HuggingFaceTask::VideoClassification => write!(f, "video-classification"),
            HuggingFaceTask::VisualQuestionAnswering => write!(f, "visual-question-answering"),
            HuggingFaceTask::ZeroShotClassification => write!(f, "zero-shot-classification"),
            HuggingFaceTask::ZeroShotImageClassification => {
                write!(f, "zero-shot-image-classification")
            }
            HuggingFaceTask::ZeroShotAudioClassification => {
                write!(f, "zero-shot-audio-classification")
            }
            HuggingFaceTask::ZeroShotObjectDetection => write!(f, "zero-shot-object-detection"),
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum HuggingFaceORTModel {
    OrtAudioClassification,
    OrtAudioFrameClassification,
    OrtAudioXVector,
    OrtCustomTasks,
    OrtCtc,
    OrtFeatureExtraction,
    OrtImageClassification,
    OrtMaskedLm,
    OrtMultipleChoice,
    OrtQuestionAnswering,
    OrtSemanticSegmentation,
    OrtSequenceClassification,
    OrtTokenClassification,
    OrtSeq2SeqLm,
    OrtSpeechSeq2Seq,
    OrtVision2Seq,
    OrtPix2Struct,
    OrtCausalLm,
    OrtOptimizer,
    OrtQuantizer,
    OrtTrainer,
    OrtSeq2SeqTrainer,
    OrtTrainingArguments,
    OrtSeq2SeqTrainingArguments,
    OrtStableDiffusionPipeline,
    OrtStableDiffusionImg2ImgPipeline,
    OrtStableDiffusionInpaintPipeline,
    OrtStableDiffusionXlPipeline,
    OrtStableDiffusionXlImg2ImgPipeline,
}

impl Display for HuggingFaceORTModel {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            HuggingFaceORTModel::OrtAudioClassification => {
                write!(f, "ORTModelForAudioClassification")
            }
            HuggingFaceORTModel::OrtAudioFrameClassification => {
                write!(f, "ORTModelForAudioFrameClassification")
            }
            HuggingFaceORTModel::OrtAudioXVector => write!(f, "ORTModelForAudioXVector"),
            HuggingFaceORTModel::OrtCustomTasks => write!(f, "ORTModelForCustomTasks"),
            HuggingFaceORTModel::OrtCtc => write!(f, "ORTModelForCTC"),
            HuggingFaceORTModel::OrtFeatureExtraction => write!(f, "ORTModelForFeatureExtraction"),
            HuggingFaceORTModel::OrtImageClassification => {
                write!(f, "ORTModelForImageClassification")
            }
            HuggingFaceORTModel::OrtMaskedLm => write!(f, "ORTModelForMaskedLM"),
            HuggingFaceORTModel::OrtMultipleChoice => write!(f, "ORTModelForMultipleChoice"),
            HuggingFaceORTModel::OrtQuestionAnswering => write!(f, "ORTModelForQuestionAnswering"),
            HuggingFaceORTModel::OrtSemanticSegmentation => {
                write!(f, "ORTModelForSemanticSegmentation")
            }
            HuggingFaceORTModel::OrtSequenceClassification => {
                write!(f, "ORTModelForSequenceClassification")
            }
            HuggingFaceORTModel::OrtTokenClassification => {
                write!(f, "ORTModelForTokenClassification")
            }
            HuggingFaceORTModel::OrtSeq2SeqLm => write!(f, "ORTModelForSeq2SeqLM"),
            HuggingFaceORTModel::OrtSpeechSeq2Seq => write!(f, "ORTModelForSpeechSeq2Seq"),
            HuggingFaceORTModel::OrtVision2Seq => write!(f, "ORTModelForVision2Seq"),
            HuggingFaceORTModel::OrtPix2Struct => write!(f, "ORTModelForPix2Struct"),
            HuggingFaceORTModel::OrtCausalLm => write!(f, "ORTModelForCausalLM"),
            HuggingFaceORTModel::OrtOptimizer => write!(f, "ORTOptimizer"),
            HuggingFaceORTModel::OrtQuantizer => write!(f, "ORTQuantizer"),
            HuggingFaceORTModel::OrtTrainer => write!(f, "ORTTrainer"),
            HuggingFaceORTModel::OrtSeq2SeqTrainer => write!(f, "ORTSeq2SeqTrainer"),
            HuggingFaceORTModel::OrtTrainingArguments => write!(f, "ORTTrainingArguments"),
            HuggingFaceORTModel::OrtSeq2SeqTrainingArguments => {
                write!(f, "ORTSeq2SeqTrainingArguments")
            }
            HuggingFaceORTModel::OrtStableDiffusionPipeline => {
                write!(f, "ORTStableDiffusionPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionImg2ImgPipeline => {
                write!(f, "ORTStableDiffusionImg2ImgPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionInpaintPipeline => {
                write!(f, "ORTStableDiffusionInpaintPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionXlPipeline => {
                write!(f, "ORTStableDiffusionXLPipeline")
            }
            HuggingFaceORTModel::OrtStableDiffusionXlImg2ImgPipeline => {
                write!(f, "ORTStableDiffusionXLImg2ImgPipeline")
            }
        }
    }
}
