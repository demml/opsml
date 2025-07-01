use crate::error::TypeError;
use pyo3::prelude::*;
use serde::{Deserialize, Deserializer, Serialize};
use std::ffi::OsStr;
use std::fmt;
use std::fmt::Display;
use std::path::{Path, PathBuf};

pub const MAX_FILE_SIZE: usize = 1024 * 1024 * 1024 * 50;

#[pyclass(eq, eq_int)]
#[derive(Debug, Eq, Hash, PartialEq, Clone, Serialize, Default)]
pub enum RegistryType {
    #[default]
    Data,
    Model,
    Experiment,
    Audit,
    Metrics,
    HardwareMetrics,
    Parameters,
    Users,
    ArtifactKey,
    Prompt,
    Deck,
}

impl<'de> Deserialize<'de> for RegistryType {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        match s.to_lowercase().as_str() {
            "data" => Ok(RegistryType::Data),
            "model" => Ok(RegistryType::Model),
            "experiment" => Ok(RegistryType::Experiment),
            "audit" => Ok(RegistryType::Audit),
            "metrics" => Ok(RegistryType::Metrics),
            "hardware_metrics" => Ok(RegistryType::HardwareMetrics),
            "parameters" => Ok(RegistryType::Parameters),
            "users" => Ok(RegistryType::Users),
            "artifact_key" => Ok(RegistryType::ArtifactKey),
            "prompt" => Ok(RegistryType::Prompt),
            "deck" => Ok(RegistryType::Deck),
            _ => Err(serde::de::Error::custom(format!(
                "Invalid registry type: {s}",
            ))),
        }
    }
}

impl Display for RegistryType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            RegistryType::Data => write!(f, "data"),
            RegistryType::Model => write!(f, "model"),
            RegistryType::Experiment => write!(f, "experiment"),
            RegistryType::Audit => write!(f, "audit"),
            RegistryType::Metrics => write!(f, "metrics"),
            RegistryType::HardwareMetrics => write!(f, "hardware_metrics"),
            RegistryType::Parameters => write!(f, "parameters"),
            RegistryType::Users => write!(f, "users"),
            RegistryType::ArtifactKey => write!(f, "artifact_key"),
            RegistryType::Prompt => write!(f, "prompt"),
            RegistryType::Deck => write!(f, "deck"),
        }
    }
}
impl RegistryType {
    pub fn from_string(s: &str) -> Result<Self, TypeError> {
        match s {
            "data" => Ok(RegistryType::Data),
            "model" => Ok(RegistryType::Model),
            "experiment" => Ok(RegistryType::Experiment),
            "audit" => Ok(RegistryType::Audit),
            "metrics" => Ok(RegistryType::Metrics),
            "hardware_metrics" => Ok(RegistryType::HardwareMetrics),
            "parameters" => Ok(RegistryType::Parameters),
            "users" => Ok(RegistryType::Users),
            "artifact_key" => Ok(RegistryType::ArtifactKey),
            "prompt" => Ok(RegistryType::Prompt),
            "deck" => Ok(RegistryType::Deck),

            _ => Err(TypeError::InvalidRegistryType),
        }
    }

    pub fn as_bytes(&self) -> &[u8] {
        match self {
            RegistryType::Data => b"data",
            RegistryType::Model => b"model",
            RegistryType::Experiment => b"experiment",
            RegistryType::Audit => b"audit",
            RegistryType::Metrics => b"metrics",
            RegistryType::HardwareMetrics => b"hardware_metrics",
            RegistryType::Parameters => b"parameters",
            RegistryType::Users => b"users",
            RegistryType::ArtifactKey => b"artifact_key",
            RegistryType::Prompt => b"prompt",
            RegistryType::Deck => b"deck",
        }
    }
}

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum PlotType {
    Line,
    Bar,
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum StorageType {
    Google,
    Aws,
    Local,
    Azure,
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum SqlType {
    Postgres,
    Sqlite,
    MySql,
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum RegistryMode {
    #[default]
    Client,
    Server,
}

impl Display for RegistryMode {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            RegistryMode::Client => write!(f, "client"),
            RegistryMode::Server => write!(f, "server"),
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone)]
pub enum UriNames {
    TrainedModelUri,
    SampleDataUri,
    PreprocessorUri,
    ModelcardUri,
    ModelMetadataUri,
    OnnxModelUri,
    DataUri,
    DatacardUri,
    ProfileUri,
    ProfileHtmlUri,
    DriftProfileUri,
    ExperimentCardUri,
    QuantizedModelUri,
    TokenizerUri,
    FeatureExtractorUri,
    OnnxConfigUri,
}

#[pymethods]
impl UriNames {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            "trained_model_uri" => Some(UriNames::TrainedModelUri),
            "sample_data_uri" => Some(UriNames::SampleDataUri),
            "preprocessor_uri" => Some(UriNames::PreprocessorUri),
            "modelcard_uri" => Some(UriNames::ModelcardUri),
            "model_metadata_uri" => Some(UriNames::ModelMetadataUri),
            "onnx_model_uri" => Some(UriNames::OnnxModelUri),
            "data_uri" => Some(UriNames::DataUri),
            "datacard_uri" => Some(UriNames::DatacardUri),
            "profile_uri" => Some(UriNames::ProfileUri),
            "profile_html_uri" => Some(UriNames::ProfileHtmlUri),
            "drift_profile_uri" => Some(UriNames::DriftProfileUri),
            "experimentcard_uri" => Some(UriNames::ExperimentCardUri),
            "quantized_model_uri" => Some(UriNames::QuantizedModelUri),
            "tokenizer_uri" => Some(UriNames::TokenizerUri),
            "feature_extractor_uri" => Some(UriNames::FeatureExtractorUri),
            "onnx_config_uri" => Some(UriNames::OnnxConfigUri),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            UriNames::TrainedModelUri => "trained_model_uri",
            UriNames::SampleDataUri => "sample_data_uri",
            UriNames::PreprocessorUri => "preprocessor_uri",
            UriNames::ModelcardUri => "modelcard_uri",
            UriNames::ModelMetadataUri => "model_metadata_uri",
            UriNames::OnnxModelUri => "onnx_model_uri",
            UriNames::DataUri => "data_uri",
            UriNames::DatacardUri => "datacard_uri",
            UriNames::ProfileUri => "profile_uri",
            UriNames::ProfileHtmlUri => "profile_html_uri",
            UriNames::DriftProfileUri => "drift_profile_uri",
            UriNames::ExperimentCardUri => "experimentcard_uri",
            UriNames::QuantizedModelUri => "quantized_model_uri",
            UriNames::TokenizerUri => "tokenizer_uri",
            UriNames::FeatureExtractorUri => "feature_extractor_uri",
            UriNames::OnnxConfigUri => "onnx_config_uri",
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Deserialize, Serialize)]
pub enum CommonKwargs {
    IsPipeline,
    ModelType,
    ModelClass,
    ModelArch,
    PreprocessorName,
    Preprocessor,
    TaskType,
    Model,
    Undefined,
    Backend,
    Pytorch,
    Tensorflow,
    SampleData,
    Onnx,
    LoadType,
    DataType,
    Tokenizer,
    TokenizerName,
    FeatureExtractor,
    FeatureExtractorName,
    Image,
    Text,
    VowpalArgs,
    BaseVersion,
    SampleDataInterfaceType,
}

#[pymethods]
impl CommonKwargs {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            "is_pipeline" => Some(CommonKwargs::IsPipeline),
            "model_type" => Some(CommonKwargs::ModelType),
            "model_class" => Some(CommonKwargs::ModelClass),
            "model_arch" => Some(CommonKwargs::ModelArch),
            "preprocessor_name" => Some(CommonKwargs::PreprocessorName),
            "preprocessor" => Some(CommonKwargs::Preprocessor),
            "task_type" => Some(CommonKwargs::TaskType),
            "model" => Some(CommonKwargs::Model),
            "undefined" => Some(CommonKwargs::Undefined),
            "backend" => Some(CommonKwargs::Backend),
            "pytorch" => Some(CommonKwargs::Pytorch),
            "tensorflow" => Some(CommonKwargs::Tensorflow),
            "sample_data" => Some(CommonKwargs::SampleData),
            "onnx" => Some(CommonKwargs::Onnx),
            "load_type" => Some(CommonKwargs::LoadType),
            "data_type" => Some(CommonKwargs::DataType),
            "tokenizer" => Some(CommonKwargs::Tokenizer),
            "tokenizer_name" => Some(CommonKwargs::TokenizerName),
            "feature_extractor" => Some(CommonKwargs::FeatureExtractor),
            "feature_extractor_name" => Some(CommonKwargs::FeatureExtractorName),
            "image" => Some(CommonKwargs::Image),
            "text" => Some(CommonKwargs::Text),
            "arguments" => Some(CommonKwargs::VowpalArgs),
            "0.0.0" => Some(CommonKwargs::BaseVersion),
            "sample_data_interface_type" => Some(CommonKwargs::SampleDataInterfaceType),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            CommonKwargs::IsPipeline => "is_pipeline",
            CommonKwargs::ModelType => "model_type",
            CommonKwargs::ModelClass => "model_class",
            CommonKwargs::ModelArch => "model_arch",
            CommonKwargs::PreprocessorName => "preprocessor_name",
            CommonKwargs::Preprocessor => "preprocessor",
            CommonKwargs::TaskType => "task_type",
            CommonKwargs::Model => "model",
            CommonKwargs::Undefined => "undefined",
            CommonKwargs::Backend => "backend",
            CommonKwargs::Pytorch => "pytorch",
            CommonKwargs::Tensorflow => "tensorflow",
            CommonKwargs::SampleData => "sample_data",
            CommonKwargs::Onnx => "onnx",
            CommonKwargs::LoadType => "load_type",
            CommonKwargs::DataType => "data_type",
            CommonKwargs::Tokenizer => "tokenizer",
            CommonKwargs::TokenizerName => "tokenizer_name",
            CommonKwargs::FeatureExtractor => "feature_extractor",
            CommonKwargs::FeatureExtractorName => "feature_extractor_name",
            CommonKwargs::Image => "image",
            CommonKwargs::Text => "text",
            CommonKwargs::VowpalArgs => "arguments",
            CommonKwargs::BaseVersion => "0.0.0",
            CommonKwargs::SampleDataInterfaceType => "sample_data_interface_type",
        }
    }
}

impl Display for CommonKwargs {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.as_string())
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone)]
pub enum SaveName {
    Card,
    Audit,
    ModelMetadata,
    Model,
    Preprocessor,
    OnnxModel,
    SampleModelData,
    DataProfile,
    Data,
    Profile,
    Artifacts,
    QuantizedModel,
    Tokenizer,
    FeatureExtractor,
    ImageProcessor,
    Metadata,
    Graphs,
    OnnxConfig,
    Dataset,
    DriftProfile,
    Drift,
    Sql,
    Code,
    Prompt,
    ReadMe,
    CardDeck,
    CardMap,
}

#[pymethods]
impl SaveName {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            "card" => Some(SaveName::Card),
            "audit" => Some(SaveName::Audit),
            "model-metadata" => Some(SaveName::ModelMetadata),
            "model" => Some(SaveName::Model),
            "preprocessor" => Some(SaveName::Preprocessor),
            "onnx-model" => Some(SaveName::OnnxModel),
            "sample-model-data" => Some(SaveName::SampleModelData),
            "data-profile" => Some(SaveName::DataProfile),
            "data" => Some(SaveName::Data),
            "profile" => Some(SaveName::Profile),
            "artifacts" => Some(SaveName::Artifacts),
            "quantized-model" => Some(SaveName::QuantizedModel),
            "tokenizer" => Some(SaveName::Tokenizer),
            "feature-extractor" => Some(SaveName::FeatureExtractor),
            "image-processor" => Some(SaveName::ImageProcessor),
            "metadata" => Some(SaveName::Metadata),
            "graphs" => Some(SaveName::Graphs),
            "onnx-config" => Some(SaveName::OnnxConfig),
            "dataset" => Some(SaveName::Dataset),
            "drift-profile" => Some(SaveName::DriftProfile),
            "sql" => Some(SaveName::Sql),
            "drift" => Some(SaveName::Drift),
            "code" => Some(SaveName::Code),
            "prompt" => Some(SaveName::Prompt),
            "README" => Some(SaveName::ReadMe),
            "card_deck" => Some(SaveName::CardDeck),
            "card_map" => Some(SaveName::CardMap),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            SaveName::Card => "card",
            SaveName::Audit => "audit",
            SaveName::ModelMetadata => "model-metadata",
            SaveName::Model => "model",
            SaveName::Preprocessor => "preprocessor",
            SaveName::OnnxModel => "onnx-model",
            SaveName::SampleModelData => "sample-model-data",
            SaveName::DataProfile => "data-profile",
            SaveName::Data => "data",
            SaveName::Profile => "profile",
            SaveName::Artifacts => "artifacts",
            SaveName::QuantizedModel => "quantized-model",
            SaveName::Tokenizer => "tokenizer",
            SaveName::FeatureExtractor => "feature-extractor",
            SaveName::ImageProcessor => "image-processor",
            SaveName::Metadata => "metadata",
            SaveName::Graphs => "graphs",
            SaveName::OnnxConfig => "onnx-config",
            SaveName::Dataset => "dataset",
            SaveName::DriftProfile => "drift-profile",
            SaveName::Sql => "sql",
            SaveName::Drift => "drift",
            SaveName::Code => "code",
            SaveName::Prompt => "prompt",
            SaveName::ReadMe => "README",
            SaveName::CardDeck => "card_deck",
            SaveName::CardMap => "card_map",
        }
    }

    pub fn __str__(&self) -> String {
        self.to_string()
    }
}

impl Display for SaveName {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.as_string())
    }
}

impl AsRef<Path> for SaveName {
    fn as_ref(&self) -> &Path {
        match self {
            SaveName::Card => Path::new("card"),
            SaveName::Audit => Path::new("audit"),
            SaveName::ModelMetadata => Path::new("model-metadata"),
            SaveName::Model => Path::new("model"),
            SaveName::Preprocessor => Path::new("preprocessor"),
            SaveName::OnnxModel => Path::new("onnx-model"),
            SaveName::SampleModelData => Path::new("sample-model-data"),
            SaveName::DataProfile => Path::new("data-profile"),
            SaveName::Data => Path::new("data"),
            SaveName::Profile => Path::new("profile"),
            SaveName::Artifacts => Path::new("artifacts"),
            SaveName::QuantizedModel => Path::new("quantized-model"),
            SaveName::Tokenizer => Path::new("tokenizer"),
            SaveName::FeatureExtractor => Path::new("feature_extractor"),
            SaveName::ImageProcessor => Path::new("image_processor"),
            SaveName::Metadata => Path::new("metadata"),
            SaveName::Graphs => Path::new("graphs"),
            SaveName::OnnxConfig => Path::new("onnx-config"),
            SaveName::Dataset => Path::new("dataset"),
            SaveName::DriftProfile => Path::new("drift-profile"),
            SaveName::Sql => Path::new("sql"),
            SaveName::Drift => Path::new("drift"),
            SaveName::Code => Path::new("code"),
            SaveName::Prompt => Path::new("prompt"),
            SaveName::ReadMe => Path::new("README"),
            SaveName::CardDeck => Path::new("card_deck"),
            SaveName::CardMap => Path::new("card_map"),
        }
    }
}

// impl PathBuf: From<SaveName>
impl From<SaveName> for PathBuf {
    fn from(save_name: SaveName) -> Self {
        PathBuf::from(save_name.as_ref())
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone)]
pub enum Suffix {
    Onnx,
    Parquet,
    Zarr,
    Joblib,
    Html,
    Json,
    Ckpt,
    Pt,
    Text,
    Catboost,
    Jsonl,
    Empty,
    Dmatrix,
    Model,
    Numpy,
    Sql,
    Bin,
    Keras,
    Md,
}

#[pymethods]
impl Suffix {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            "onnx" => Some(Suffix::Onnx),
            "parquet" => Some(Suffix::Parquet),
            "zarr" => Some(Suffix::Zarr),
            "joblib" => Some(Suffix::Joblib),
            "html" => Some(Suffix::Html),
            "json" => Some(Suffix::Json),
            "ckpt" => Some(Suffix::Ckpt),
            "pt" => Some(Suffix::Pt),
            "txt" => Some(Suffix::Text),
            "cbm" => Some(Suffix::Catboost),
            "jsonl" => Some(Suffix::Jsonl),
            "" => Some(Suffix::Empty),
            "dmatrix" => Some(Suffix::Dmatrix),
            "model" => Some(Suffix::Model),
            "npy" => Some(Suffix::Numpy),
            "sql" => Some(Suffix::Sql),
            "bin" => Some(Suffix::Bin),
            "keras" => Some(Suffix::Keras),
            "md" => Some(Suffix::Md),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            Suffix::Onnx => "onnx",
            Suffix::Parquet => "parquet",
            Suffix::Zarr => "zarr",
            Suffix::Joblib => "joblib",
            Suffix::Html => "html",
            Suffix::Json => "json",
            Suffix::Ckpt => "ckpt",
            Suffix::Pt => "pt",
            Suffix::Text => "txt",
            Suffix::Catboost => "cbm",
            Suffix::Jsonl => "jsonl",
            Suffix::Empty => "",
            Suffix::Dmatrix => "dmatrix",
            Suffix::Model => "model",
            Suffix::Numpy => "npy",
            Suffix::Sql => "sql",
            Suffix::Bin => "bin",
            Suffix::Keras => "keras",
            Suffix::Md => "md",
        }
    }

    pub fn __str__(&self) -> String {
        self.to_string()
    }
}

impl Display for Suffix {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.as_string())
    }
}

impl AsRef<OsStr> for Suffix {
    fn as_ref(&self) -> &OsStr {
        OsStr::new(self.as_string())
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone)]
pub enum ArtifactClass {
    Data,
    Other,
}

#[pymethods]
impl ArtifactClass {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            "data" => Some(ArtifactClass::Data),
            "other" => Some(ArtifactClass::Other),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            ArtifactClass::Data => "data",
            ArtifactClass::Other => "other",
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone)]
pub enum PresignableTypes {
    Jpeg,
    Jpg,
    Png,
    Pdf,
    Md,
    Text,
    Csv,
    Json,
    Tiff,
    Gif,
    Mp4,
    Py,
    Yml,
    Yaml,
}

#[pymethods]
impl PresignableTypes {
    #[staticmethod]
    pub fn from_string(s: &str) -> Option<Self> {
        match s {
            ".jpeg" => Some(PresignableTypes::Jpeg),
            ".jpg" => Some(PresignableTypes::Jpg),
            ".png" => Some(PresignableTypes::Png),
            ".pdf" => Some(PresignableTypes::Pdf),
            ".md" => Some(PresignableTypes::Md),
            ".txt" => Some(PresignableTypes::Text),
            ".csv" => Some(PresignableTypes::Csv),
            ".json" => Some(PresignableTypes::Json),
            ".tiff" => Some(PresignableTypes::Tiff),
            ".gif" => Some(PresignableTypes::Gif),
            ".mp4" => Some(PresignableTypes::Mp4),
            ".py" => Some(PresignableTypes::Py),
            ".yml" => Some(PresignableTypes::Yml),
            ".yaml" => Some(PresignableTypes::Yaml),
            _ => None,
        }
    }

    pub fn as_string(&self) -> &str {
        match self {
            PresignableTypes::Jpeg => ".jpeg",
            PresignableTypes::Jpg => ".jpg",
            PresignableTypes::Png => ".png",
            PresignableTypes::Pdf => ".pdf",
            PresignableTypes::Md => ".md",
            PresignableTypes::Text => ".txt",
            PresignableTypes::Csv => ".csv",
            PresignableTypes::Json => ".json",
            PresignableTypes::Tiff => ".tiff",
            PresignableTypes::Gif => ".gif",
            PresignableTypes::Mp4 => ".mp4",
            PresignableTypes::Py => ".py",
            PresignableTypes::Yml => ".yml",
            PresignableTypes::Yaml => ".yaml",
        }
    }
}

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum DataType {
    Pandas,
    Arrow,
    Polars,
    Numpy,
    Image,
    Text,
    Dict,
    Sql,
    Profile,
    TransformerBatch,
    String,
    TorchTensor,
    TorchDataset,
    TensorFlowTensor,
    DMatrix,
    Tuple,
    List,
    Str,
    OrderedDict,
    Joblib,
    Base,
    Dataset,

    #[default]
    NotProvided,
}

impl Display for DataType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            DataType::Pandas => write!(f, "Pandas"),
            DataType::Arrow => write!(f, "Arrow"),
            DataType::Polars => write!(f, "Polars"),
            DataType::Numpy => write!(f, "Numpy"),
            DataType::Image => write!(f, "Image"),
            DataType::Text => write!(f, "Text"),
            DataType::Dict => write!(f, "Dict"),
            DataType::Sql => write!(f, "Sql"),
            DataType::Profile => write!(f, "Profile"),
            DataType::TransformerBatch => write!(f, "TransformerBatch"),
            DataType::String => write!(f, "string"),
            DataType::TorchTensor => write!(f, "TorchTensor"),
            DataType::TorchDataset => write!(f, "TorchDataset"),
            DataType::TensorFlowTensor => write!(f, "TensorFlowTensor"),
            DataType::DMatrix => write!(f, "DMatrix"),
            DataType::Tuple => write!(f, "Tuple"),
            DataType::List => write!(f, "List"),
            DataType::Str => write!(f, "str"),
            DataType::OrderedDict => write!(f, "OrderedDict"),
            DataType::Joblib => write!(f, "Joblib"),
            DataType::Base => write!(f, "Base"),
            DataType::Dataset => write!(f, "Dataset"),
            DataType::NotProvided => write!(f, "NotProvided"),
        }
    }
}

pub type BaseArgsType = (String, String, String, String);

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub enum InterfaceType {
    Data,
    Model,
}

#[pyclass]
pub struct SaverPath {
    #[pyo3(get)]
    path: PathBuf,
}

#[pymethods]
impl SaverPath {
    #[new]
    #[pyo3(signature = (parent, child=None, filename=None, extension=None))]
    pub fn new(
        parent: PathBuf,
        child: Option<PathBuf>,
        filename: Option<SaveName>,
        extension: Option<Suffix>,
    ) -> Self {
        // if child_path is not none, append it to the parent path and create all directories if they do not exist
        let mut build_path = match &child {
            Some(child) => {
                let mut path = parent.clone();
                path.push(child);
                if !path.exists() {
                    std::fs::create_dir_all(&path).unwrap();
                }
                path
            }
            None => parent.clone(),
        };

        // if file_name is not none, append it to the parent path with the extension
        if let Some(file_name) = filename {
            build_path.push(file_name);
            if let Some(extension) = extension {
                build_path.set_extension(extension);
            }
        }

        SaverPath { path: build_path }
    }
}

#[derive(Debug, Clone)]
pub enum IntegratedService {
    Scouter,
}

impl Display for IntegratedService {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            IntegratedService::Scouter => write!(f, "scouter"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_uri_names_from_string() {
        assert_eq!(
            UriNames::from_string("trained_model_uri"),
            Some(UriNames::TrainedModelUri)
        );
        assert_eq!(
            UriNames::from_string("sample_data_uri"),
            Some(UriNames::SampleDataUri)
        );
        assert_eq!(UriNames::from_string("invalid_uri"), None);
    }

    #[test]
    fn test_uri_names_as_str() {
        assert_eq!(UriNames::TrainedModelUri.as_string(), "trained_model_uri");
        assert_eq!(UriNames::SampleDataUri.as_string(), "sample_data_uri");
    }

    #[test]
    fn test_common_kwargs_from_str() {
        assert_eq!(
            CommonKwargs::from_string("is_pipeline"),
            Some(CommonKwargs::IsPipeline)
        );
        assert_eq!(
            CommonKwargs::from_string("model_type"),
            Some(CommonKwargs::ModelType)
        );
        assert_eq!(CommonKwargs::from_string("invalid_kwarg"), None);
    }

    #[test]
    fn test_common_kwargs_as_str() {
        assert_eq!(CommonKwargs::IsPipeline.as_string(), "is_pipeline");
        assert_eq!(CommonKwargs::ModelType.as_string(), "model_type");
    }

    #[test]
    fn test_save_name_from_str() {
        assert_eq!(SaveName::from_string("card"), Some(SaveName::Card));
        assert_eq!(SaveName::from_string("audit"), Some(SaveName::Audit));
        assert_eq!(SaveName::from_string("invalid_save_name"), None);
    }

    #[test]
    fn test_save_name_as_str() {
        assert_eq!(SaveName::Card.as_string(), "card");
        assert_eq!(SaveName::Audit.as_string(), "audit");
    }

    #[test]
    fn test_suffix_from_str() {
        assert_eq!(Suffix::from_string("onnx"), Some(Suffix::Onnx));
        assert_eq!(Suffix::from_string("parquet"), Some(Suffix::Parquet));
        assert_eq!(Suffix::from_string("invalid_suffix"), None);
    }

    #[test]
    fn test_suffix_as_str() {
        assert_eq!(Suffix::Onnx.as_string(), "onnx");
        assert_eq!(Suffix::Parquet.as_string(), "parquet");
    }

    #[test]
    fn test_artifact_class_from_str() {
        assert_eq!(
            ArtifactClass::from_string("data"),
            Some(ArtifactClass::Data)
        );
        assert_eq!(
            ArtifactClass::from_string("other"),
            Some(ArtifactClass::Other)
        );
        assert_eq!(ArtifactClass::from_string("invalid_class"), None);
    }

    #[test]
    fn test_artifact_class_as_str() {
        assert_eq!(ArtifactClass::Data.as_string(), "data");
        assert_eq!(ArtifactClass::Other.as_string(), "other");
    }

    #[test]
    fn test_presignable_types_from_str() {
        assert_eq!(
            PresignableTypes::from_string(".jpeg"),
            Some(PresignableTypes::Jpeg)
        );
        assert_eq!(
            PresignableTypes::from_string(".jpg"),
            Some(PresignableTypes::Jpg)
        );
        assert_eq!(PresignableTypes::from_string(".invalid_type"), None);
    }

    #[test]
    fn test_presignable_types_as_str() {
        assert_eq!(PresignableTypes::Jpeg.as_string(), ".jpeg");
        assert_eq!(PresignableTypes::Jpg.as_string(), ".jpg");
    }
}
